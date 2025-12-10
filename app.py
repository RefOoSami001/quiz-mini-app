from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import pdfplumber
from io import BytesIO
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
api_service2 = MCQGeneratorAPI2()
api_service3 = MCQGeneratorAPI3()

# Initialize Telegram bot for sending polls
bot = telebot.TeleBot(BOT_TOKEN, threaded=True)
ADMIN_CHAT_ID = 854578633  # Admin Telegram user ID to receive notifications

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

@app.route('/favicon.ico')
def favicon():
    # Return empty 204 to avoid 404 spam in logs
    return ('', 204)

@app.route('/api/notify-open', methods=['POST'])
def notify_open():
    try:
        data = request.get_json(silent=True) or {}
        session_id = data.get('session_id')
        user = data.get('user') or {}
        user_id = user.get('id')
        username = user.get('username')
        first_name = user.get('first_name')
        last_name = user.get('last_name')

        display_name = None
        if username:
            display_name = f"@{username}"
        elif first_name or last_name:
            display_name = " ".join([n for n in [first_name, last_name] if n])
        elif user_id:
            display_name = str(user_id)

        msg_lines = ["Mini app opened"]
        if display_name:
            msg_lines.append(f"User: {display_name}")
        if user_id:
            msg_lines.append(f"User ID: {user_id}")
        if session_id:
            msg_lines.append(f"Session: {session_id}")

        try:
            bot.send_message(ADMIN_CHAT_ID, "\n".join(msg_lines))
        except Exception as e:
            # Avoid failing client if bot can't send
            print(f"Notify open send_message error: {e}")

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/generate-questions', methods=['POST'])
def generate_questions():
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        model = data.get('model', '2')
        text = data.get('text', '')
        question_count = data.get('question_count', 10)
        question_type = data.get('question_type')  # for model 3: 'true/false' or 'Multiple Choice'
        
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
            if question_type:
                user_sessions[session_id]['question_type'] = question_type

        # Generate questions asynchronously
        def _generate():
            try:
                success = False
                result = None
                
                if model == '2':
                    success, result = api_service2.generate_questions(text, question_count)
                elif model == '3':
                    qt = question_type or user_sessions.get(session_id, {}).get('question_type') or 'Multiple Choice'
                    success, result = api_service3.generate_questions(text, question_count, qt)
                    # Normalize API3 responses into a unified list of {question, options, correct, explanation}
                    try:
                        normalized = []
                        questions = result.get('questions') if isinstance(result, dict) else None
                        if isinstance(questions, list):
                            # Get question type from session to help determine format
                            session_qt = qt.lower()
                            is_short_answer = 'short' in session_qt or 'short_answer' in session_qt
                            
                            for q in questions:
                                # Handle new API format: uses 'answer' instead of 'correct_answer'
                                answer_key = 'answer' if 'answer' in q else 'correct_answer'
                                
                                if 'options' in q and answer_key in q:
                                    # Multiple Choice: handle both formats
                                    opts_raw = q.get('options', [])
                                    correct_text = q.get(answer_key)
                                    correct_index = 0
                                    opts = []
                                    
                                    # Check if options is a list of objects (new format) or strings (old format)
                                    if opts_raw and len(opts_raw) > 0 and isinstance(opts_raw[0], dict):
                                        # New format: [{'label': 'A', 'text': '...', 'is_correct': True/False}, ...]
                                        for idx, opt_obj in enumerate(opts_raw):
                                            label = opt_obj.get('label', '')
                                            opt_text = opt_obj.get('text', '')
                                            is_correct = opt_obj.get('is_correct', False)
                                            
                                            # Format as "A) Text" or just "Text" if no label
                                            if label:
                                                opt_str = f"{label}) {opt_text}" if opt_text else label
                                            else:
                                                opt_str = opt_text if opt_text else ''
                                            opts.append(opt_str)
                                            
                                            # Find correct index: prioritize is_correct flag, then match answer text
                                            if is_correct:
                                                correct_index = idx
                                            elif correct_text and opt_text and correct_text.strip().lower() == opt_text.strip().lower():
                                                correct_index = idx
                                    else:
                                        # Old format: ["A) ...", "B) ...", ...]
                                        opts = opts_raw if opts_raw else []
                                        for idx, opt in enumerate(opts):
                                            if opt == correct_text or (isinstance(opt, str) and correct_text and correct_text in opt):
                                                correct_index = idx
                                                break
                                    
                                    if opts:  # Only add if we have valid options
                                        normalized.append({
                                            'question': q.get('question', ''),
                                            'options': opts,
                                            'correct': correct_index,
                                            'explanation': ''
                                        })
                                elif answer_key in q and 'question' in q:
                                    answer_value = str(q.get(answer_key, '')).strip()
                                    
                                    if is_short_answer or ('options' not in q and len(answer_value) > 10):
                                        # Short Answer: has answer but no options, or answer is long (not True/False)
                                        normalized.append({
                                            'question': q.get('question', ''),
                                            'options': [],  # Empty options indicates short answer
                                            'correct': -1,  # No correct index for short answer
                                            'answer': answer_value,  # Store the answer text
                                            'explanation': ''
                                        })
                                    else:
                                        # True/False: answer is 'True' or 'False', create options ["True","False"]
                                        correct_bool = answer_value.lower() in ['true', 't', '1']
                                        opts = ['True', 'False']
                                        correct_index = 0 if correct_bool else 1
                                        normalized.append({
                                            'question': q.get('question', ''),
                                            'options': opts,
                                            'correct': correct_index,
                                            'explanation': ''
                                        })
                        if normalized:
                            result = normalized
                        else:
                            # If no questions were normalized, mark as failed
                            success = False
                            result = 'No valid questions could be generated from your material.'
                    except Exception as e:
                        success = False
                        result = f'Error processing questions: {str(e)}'
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
                if not question.get('question'):
                    skipped_count += 1
                    continue
                
                # Skip if question text is too long
                if len(question['question']) > 300:
                    skipped_count += 1
                    continue
                
                # Check if it's a short answer question (no options or empty options)
                options = question.get('options', [])
                is_short_answer = len(options) == 0 or question.get('correct') == -1
                
                if is_short_answer:
                    # Send as text message for short answer questions
                    answer = question.get('answer', 'No answer provided')
                    message = f"❓ {question['question']}\n\n✅ Answer: {answer}"
                    bot.send_message(user_id, message)
                    sent_count += 1
                else:
                    # Multiple Choice or True/False: send as poll
                    if len(options) < 2:
                        skipped_count += 1
                        continue
                    
                    # Filter out answers that are too long
                    valid_options = []
                    for option in options:
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
