from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import pdfplumber
from io import BytesIO
from api_service import MCQGeneratorAPI
from api_service2 import MCQGeneratorAPI2
from api_service3 import MCQGeneratorAPI3
from config import MIN_TEXT_LENGTH, BOT_TOKEN
import telebot
from telebot import types
import threading
import gc
from concurrent.futures import ThreadPoolExecutor
import random
import re
import json
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize API services
api_service1 = MCQGeneratorAPI()
api_service2 = MCQGeneratorAPI2()
api_service3 = MCQGeneratorAPI3()

# Initialize Telegram bot for sending polls
bot = telebot.TeleBot(BOT_TOKEN, threaded=True)

# Admin chat ID for notifications
ADMIN_CHAT_ID = int(os.getenv('ADMIN_CHAT_ID', '854578633'))

# Thread pool for handling question generation
executor = ThreadPoolExecutor(max_workers=10)

# Store user sessions
user_sessions = {}
session_lock = threading.Lock()

# Allowed file extensions
ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/notify', methods=['POST'])
def notify_admin():
    """
    Notify the admin via Telegram about app events.
    Expected JSON body:
      {
        "event": "app_started|generation_requested|generation_completed|error|pdf_processed|sent_to_telegram|custom",
        "payload": { ... arbitrary ... }
      }
    """
    try:
        data = request.get_json() or {}
        event = data.get('event', 'unknown_event')
        payload = data.get('payload', {})

        # Extract common user fields if provided
        user_id = payload.get('user_id') or payload.get('telegram_user_id')
        user_name = payload.get('user_name') or payload.get('name')
        session_id = payload.get('session_id')

        # Build a readable message
        lines = []
        lines.append(f"Event: {event}")
        if session_id:
            lines.append(f"Session: {session_id}")
        if user_id is not None:
            lines.append(f"User ID: {user_id}")
        if user_name:
            lines.append(f"User: {user_name}")

        # Add small set of known fields if present
        for key in [
            'model', 'question_count', 'count', 'page_range', 'error', 'status',
            'sent', 'skipped'
        ]:
            if key in payload and payload[key] is not None:
                lines.append(f"{key.replace('_',' ').title()}: {payload[key]}")

        # Fallback: include remaining payload keys compactly
        extra = {k: v for k, v in payload.items() if k not in ['user_id','telegram_user_id','user_name','name','session_id','model','question_count','count','page_range','error','status','sent','skipped']}
        if extra:
            try:
                lines.append(f"Payload: {json.dumps(extra)[:800]}")
            except Exception:
                pass

        message = "\n".join(lines)

        # Send to admin
        try:
            bot.send_message(ADMIN_CHAT_ID, message)
        except Exception as e:
            # Return 200 but indicate telegram error
            return jsonify({
                'success': False,
                'error': f'Telegram send error: {str(e)}'
            }), 200

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/generate-questions', methods=['POST'])
def generate_questions():
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        model = data.get('model', '1')
        text = data.get('text', '')
        question_count = data.get('question_count', 10)
        question_type = data.get('question_type')  # only required for model 3
        
        if not text or len(text) < MIN_TEXT_LENGTH:
            return jsonify({
                'success': False,
                'error': 'Text is too short. Please provide more content.'
            }), 400
        
        # Store session data
        with session_lock:
            if session_id not in user_sessions:
                user_sessions[session_id] = {}
            user_sessions[session_id]['model'] = model
            user_sessions[session_id]['question_count'] = question_count
        
        # Generate questions asynchronously
        def _generate():
            try:
                success = False
                result = None
                
                if model == '1':
                    success, result = api_service1.generate_questions(text)
                elif model == '2':
                    success, result = api_service2.generate_questions(text, question_count)
                elif model == '3':
                    # Fallbacks
                    qtype = question_type or 'Multiple Choice'
                    success, result = api_service3.generate_questions(text, question_count, qtype)
                else:
                    success, result = False, 'Unknown model'
                
                # Store result in session
                with session_lock:
                    if session_id in user_sessions:
                        user_sessions[session_id]['questions'] = result if success else None
                        user_sessions[session_id]['generation_success'] = success
                        user_sessions[session_id]['generation_error'] = result if not success else None
                
            except Exception as e:
                with session_lock:
                    if session_id in user_sessions:
                        user_sessions[session_id]['generation_success'] = False
                        user_sessions[session_id]['generation_error'] = str(e)
        
        executor.submit(_generate)
        
        return jsonify({
            'success': True,
            'message': 'Question generation started. Please wait...'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/check-generation-status', methods=['POST'])
def check_generation_status():
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        
        with session_lock:
            session_data = user_sessions.get(session_id, {})
            
            if 'generation_success' not in session_data:
                return jsonify({
                    'status': 'processing',
                    'message': 'Generating questions...'
                })
            
            if session_data['generation_success']:
                questions = session_data.get('questions', [])
                return jsonify({
                    'status': 'completed',
                    'questions': questions,
                    'count': len(questions) if isinstance(questions, (list, dict)) else 0
                })
            else:
                error = session_data.get('generation_error', 'Unknown error')
                return jsonify({
                    'status': 'error',
                    'error': error
                })
                
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/api/process-pdf', methods=['POST'])
def process_pdf():
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400
        
        file = request.files['file']
        session_id = request.form.get('session_id')
        page_range = request.form.get('page_range', '1-1')
        
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'error': 'Only PDF files are allowed'}), 400
        
        # Parse page range
        try:
            if '-' in page_range:
                start_page, end_page = map(int, page_range.split('-'))
            else:
                start_page = end_page = int(page_range)
        except ValueError:
            return jsonify({'success': False, 'error': 'Invalid page range format'}), 400
        
        # Process PDF
        try:
            file_content = file.read()
            text_content = ""
            
            with BytesIO(file_content) as pdf_stream:
                with pdfplumber.open(pdf_stream) as pdf:
                    num_pages = len(pdf.pages)
                    
                    # Validate page range
                    if start_page < 1 or end_page > num_pages or start_page > end_page:
                        return jsonify({
                            'success': False, 
                            'error': f'Invalid page range. Document has {num_pages} pages.'
                        }), 400
                    
                    # Extract text from specified pages
                    for page_num in range(start_page - 1, end_page):
                        text_content += pdf.pages[page_num].extract_text() + "\n"
            
            if len(text_content) < MIN_TEXT_LENGTH:
                return jsonify({
                    'success': False,
                    'error': 'Extracted text is too short. Please select more pages or try a different document.'
                }), 400
            
            # Store extracted text in session
            with session_lock:
                if session_id not in user_sessions:
                    user_sessions[session_id] = {}
                user_sessions[session_id]['extracted_text'] = text_content
            
            return jsonify({
                'success': True,
                'text': text_content,
                'message': f'Successfully extracted text from pages {start_page}-{end_page}'
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Error processing PDF: {str(e)}'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/get-session-data', methods=['POST'])
def get_session_data():
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        
        with session_lock:
            session_data = user_sessions.get(session_id, {})
            return jsonify({
                'success': True,
                'data': session_data
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/clear-session', methods=['POST'])
def clear_session():
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        
        with session_lock:
            if session_id in user_sessions:
                del user_sessions[session_id]
        
        return jsonify({
            'success': True,
            'message': 'Session cleared'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/send-to-telegram', methods=['POST'])
def send_to_telegram():
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        questions = data.get('questions', [])
        user_id = data.get('user_id')
        
        if not questions:
            return jsonify({
                'success': False,
                'error': 'No questions to send'
            }), 400
        
        if not user_id:
            return jsonify({
                'success': False,
                'error': 'User ID not provided'
            }), 400
        
        # Send questions as polls to the user
        sent_count = 0
        skipped_count = 0
        
        for question in questions:
            try:
                # Validate question
                if not question.get('question') or not question.get('options') or len(question.get('options', [])) < 2:
                    skipped_count += 1
                    continue
                
                # Skip if question text is too long
                if len(question['question']) > 300:
                    skipped_count += 1
                    continue
                
                # Filter out answers that are too long
                valid_options = []
                for option in question['options']:
                    if len(option) <= 100:
                        valid_options.append(option)
                
                if len(valid_options) < 2:
                    skipped_count += 1
                    continue
                
                # Send poll
                bot.send_poll(
                    user_id,
                    question['question'],
                    options=valid_options,
                    is_anonymous=True,
                    type='quiz',
                    correct_option_id=question.get('correct', 0),
                    explanation=question.get('explanation', '')
                )
                sent_count += 1
                
            except Exception as e:
                print(f"Error sending question: {e}")
                skipped_count += 1
                continue
        
        return jsonify({
            'success': True,
            'message': f'Sent {sent_count} questions to Telegram',
            'sent': sent_count,
            'skipped': skipped_count
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
