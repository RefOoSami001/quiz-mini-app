import os
import telebot
from telebot import types
import pdfplumber
from keep_alive import keep_alive
from io import BytesIO
from api_service import MCQGeneratorAPI
from api_service2 import MCQGeneratorAPI2
from config import (
    BOT_TOKEN, DIFFICULTY_LEVELS, MESSAGES,
    QUESTION_COUNTS, MIN_TEXT_LENGTH, ADMIN_CHAT_ID
)
import threading
import gc
from concurrent.futures import ThreadPoolExecutor
import random
import re

# Initialize bot and API services with threading support
bot = telebot.TeleBot(BOT_TOKEN, threaded=True)
api_service1 = MCQGeneratorAPI()
api_service2 = MCQGeneratorAPI2()

# Store user data
user_data = {}
user_data_lock = threading.Lock()

# Thread pool for handling question generation
executor = ThreadPoolExecutor(max_workers=10)

def get_text(text_key, *format_args):
    """Get text in English."""
    text = MESSAGES['en'].get(text_key, "")
    if format_args:
        return text.format(*format_args)
    return text

def create_main_menu():
    """Create main menu."""
    markup = types.InlineKeyboardMarkup(row_width=2)
    create_mcq_btn = types.InlineKeyboardButton(get_text('create_mcq'), callback_data='create_mcq')
    contact_dev_btn = types.InlineKeyboardButton(get_text('contact_dev'), callback_data='contact_dev')
    help_btn = types.InlineKeyboardButton(get_text('help_btn'), callback_data='help')
    
    markup.add(create_mcq_btn, contact_dev_btn)
    markup.add(help_btn)
    return markup

def create_model_selection_menu():
    """Create model selection menu."""
    markup = types.InlineKeyboardMarkup(row_width=2)
    model1_btn = types.InlineKeyboardButton(get_text('model1'), callback_data='model_1')
    model2_btn = types.InlineKeyboardButton(get_text('model2'), callback_data='model_2')
    
    markup.add(model1_btn, model2_btn)
    return markup

def create_question_count_menu():
    """Create question count menu."""
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = []
    
    for count, text in QUESTION_COUNTS['en'].items():
        buttons.append(types.InlineKeyboardButton(text, callback_data=f'count_{count}'))
    
    for i in range(0, len(buttons), 2):
        if i + 1 < len(buttons):
            markup.add(buttons[i], buttons[i+1])
        else:
            markup.add(buttons[i])
    
    return markup

def create_input_type_menu():
    """Create input type menu."""
    markup = types.InlineKeyboardMarkup(row_width=2)
    text_btn = types.InlineKeyboardButton(get_text('text_btn'), callback_data='send_text')
    pdf_btn = types.InlineKeyboardButton(get_text('pdf_btn'), callback_data='send_pdf')
    
    markup.add(text_btn, pdf_btn)
    return markup

def notify_admin(message, user=None):
    """Send notification to admin."""
    try:
        if user:
            user_info = f"User ID: {user.id}\n"
            user_info += f"Username: @{user.username}\n" if user.username else "Username: None\n"
            user_info += f"First Name: {user.first_name}\n" if user.first_name else ""
            user_info += f"Last Name: {user.last_name}\n" if user.last_name else ""
            user_info += f"Language Code: {user.language_code}\n" if user.language_code else ""
            
            bot.send_message(
                ADMIN_CHAT_ID,
                f"🔔 Bot Notification\n\n{message}\n\nUser Information:\n{user_info}",
                parse_mode=None
            )
        else:
            bot.send_message(
                ADMIN_CHAT_ID,
                f"🔔 Bot Notification\n\n{message}",
                parse_mode=None
            )
    except Exception as e:
        print(f"Failed to notify admin: {e}")

@bot.message_handler(commands=['start'])
def start(message):
    notify_admin("New user started the bot", message.from_user)
    bot.send_message(
        message.chat.id,
        get_text('welcome'),
        parse_mode='Markdown',
        reply_markup=create_main_menu()
    )

@bot.callback_query_handler(func=lambda call: call.data == 'help')
def help_callback(call):
    bot.edit_message_text(
        get_text('help'),
        call.message.chat.id,
        call.message.message_id,
        parse_mode='Markdown',
        reply_markup=create_main_menu()
    )

@bot.callback_query_handler(func=lambda call: call.data == 'contact_dev')
def contact_dev_callback(call):
    bot.edit_message_text(
        get_text('contact'),
        call.message.chat.id,
        call.message.message_id,
        parse_mode='Markdown',
        reply_markup=create_main_menu()
    )

@bot.callback_query_handler(func=lambda call: call.data == 'create_mcq')
def create_mcq_callback(call):
    bot.edit_message_text(
        get_text('model_selection'),
        call.message.chat.id,
        call.message.message_id,
        parse_mode='Markdown',
        reply_markup=create_model_selection_menu()
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('model_'))
def model_selection_callback(call):
    model = call.data.split('_')[1]
    chat_id = call.message.chat.id
    
    # Store the selected model
    with user_data_lock:
        if chat_id not in user_data:
            user_data[chat_id] = {}
        user_data[chat_id]['model'] = model
    
    if model == '2':
        # For model 2, ask for question count
        bot.edit_message_text(
            get_text('question_count'),
            chat_id,
            call.message.message_id,
            parse_mode='Markdown',
            reply_markup=create_question_count_menu()
        )
    else:
        # For model 1, go directly to input type selection
        bot.edit_message_text(
            get_text('input_method'),
            chat_id,
            call.message.message_id,
            parse_mode='Markdown',
            reply_markup=create_input_type_menu()
        )

@bot.callback_query_handler(func=lambda call: call.data.startswith('count_'))
def question_count_callback(call):
    count = int(call.data.split('_')[1])
    chat_id = call.message.chat.id
    
    # Store the selected question count
    with user_data_lock:
        if chat_id not in user_data:
            user_data[chat_id] = {}
        user_data[chat_id]['question_count'] = count
    
    # Ask for input type
    bot.edit_message_text(
        get_text('input_method'),
        chat_id,
        call.message.message_id,
        parse_mode='Markdown',
        reply_markup=create_input_type_menu()
    )

@bot.callback_query_handler(func=lambda call: call.data == 'send_text')
def send_text_callback(call):
    chat_id = call.message.chat.id
    
    # Set state to waiting for text
    with user_data_lock:
        if chat_id not in user_data:
            user_data[chat_id] = {}
        user_data[chat_id]['waiting_for'] = 'text'
    
    bot.edit_message_text(
        get_text('send_text'),
        chat_id,
        call.message.message_id,
        parse_mode='Markdown'
    )

@bot.callback_query_handler(func=lambda call: call.data == 'send_pdf')
def send_pdf_callback(call):
    chat_id = call.message.chat.id
    
    # Set state to waiting for PDF
    with user_data_lock:
        if chat_id not in user_data:
            user_data[chat_id] = {}
        user_data[chat_id]['waiting_for'] = 'pdf'
    
    bot.edit_message_text(
        get_text('send_pdf'),
        chat_id,
        call.message.message_id,
        parse_mode='Markdown'
    )

@bot.message_handler(content_types=['document'])
def handle_document(message):
    chat_id = message.chat.id
    
    # Check if user is waiting for PDF
    with user_data_lock:
        waiting_for = user_data.get(chat_id, {}).get('waiting_for')
        if waiting_for != 'pdf':
            return

    if not message.document.file_name.endswith('.pdf'):
        bot.send_message(
            chat_id,
            get_text('invalid_pdf')
        )
        return

    # Store only file_id without downloading yet
    file_id = message.document.file_id
    
    # Store file_id
    with user_data_lock:
        if chat_id not in user_data:
            user_data[chat_id] = {}
        user_data[chat_id]['file_id'] = file_id
        user_data[chat_id]['waiting_for'] = 'page_range'
    
    # Ask for page range directly
    bot.send_message(
        chat_id,
        "Please send the page range you want to extract (e.g., 1-5):"
    )

@bot.message_handler(func=lambda message: user_data.get(message.chat.id, {}).get('waiting_for') == 'page_range')
def handle_page_range(message):
    chat_id = message.chat.id
    
    # Get user data
    with user_data_lock:
        if chat_id not in user_data:
            return
        user_info = user_data[chat_id]
        file_id = user_info.get('file_id')
    
    if not file_id:
        bot.send_message(
            chat_id,
            get_text('error', "PDF file reference not found")
        )
        return
        
    # Send processing message
    processing_msg = bot.send_message(
        chat_id,
        get_text('processing_pdf')
    )
    
    try:
        # Parse page range first so we don't download if range is invalid
        if '-' in message.text:
            start_page, end_page = map(int, message.text.split('-'))
        else:
            # If user enters a single number, use it as both start and end
            start_page = end_page = int(message.text)
            
        # Now download the PDF and get page count and extract text in one operation
        file_info = bot.get_file(file_id)
        text_content = ""
        
        try:
            with BytesIO(bot.download_file(file_info.file_path)) as pdf_stream:
                with pdfplumber.open(pdf_stream) as pdf:
                    # Check page count and validate range
                    num_pages = len(pdf.pages)
                    
                    # Validate page range
                    if start_page < 1 or end_page > num_pages or start_page > end_page:
                        bot.edit_message_text(
                            f"⚠️ Invalid page range. The document has {num_pages} pages. Please send a valid range.",
                            chat_id,
                            processing_msg.message_id
                        )
                        return
                    
                    # Update processing message
                    bot.edit_message_text(
                        get_text('extracting_text'),
                        chat_id,
                        processing_msg.message_id
                    )
                    
                    # For larger documents, process pages in smaller batches
                    batch_size = 5  # Process 5 pages at a time to avoid memory issues
                    pages_remaining = end_page - start_page + 1
                    current_page = start_page - 1  # 0-indexed for pdfplumber
                    
                    while pages_remaining > 0:
                        # Calculate batch
                        batch_pages = min(batch_size, pages_remaining)
                        batch_end = current_page + batch_pages
                        
                        # Process this batch of pages
                        for page_num in range(current_page, batch_end):
                            text_content += pdf.pages[page_num].extract_text() + "\n"
                        
                        # Update progress for large documents
                        if pages_remaining > batch_size:
                            progress = int(((end_page - start_page + 1) - pages_remaining) / (end_page - start_page + 1) * 100)
                            bot.edit_message_text(
                                f"⏳ Extracting text... {progress}% complete",
                                chat_id,
                                processing_msg.message_id
                            )
                        
                        # Update counters
                        current_page += batch_pages
                        pages_remaining -= batch_pages
                        
                        # Force garbage collection after each batch
                        gc.collect()
            
            # Check text length
            if len(text_content) < MIN_TEXT_LENGTH:
                bot.edit_message_text(
                    get_text('text_too_short'),
                    chat_id,
                    processing_msg.message_id,
                    parse_mode='Markdown'
                )
                return
            
            # Update processing message
            bot.edit_message_text(
                get_text('text_extracted'),
                chat_id,
                processing_msg.message_id
            )
            
            # Generate questions
            generate_questions_async(chat_id, text_content, processing_msg)
            
            # Clean up PDF data - remove file_id reference
            with user_data_lock:
                if chat_id in user_data:
                    user_data[chat_id].pop('file_id', None)
            
            # Clean up text content
            del text_content
            gc.collect()
            
        except Exception as e:
            bot.edit_message_text(
                get_text('error', str(e)),
                chat_id,
                processing_msg.message_id
            )
            notify_admin(f"Error processing PDF: {str(e)}")
            
    except (ValueError, IndexError):
        bot.send_message(
            chat_id,
            get_text('invalid_range')
        )

@bot.message_handler(func=lambda message: user_data.get(message.chat.id, {}).get('waiting_for') == 'text')
def handle_text_input(message):
    chat_id = message.chat.id
    text = message.text
    
    # Check text length
    if len(text) < MIN_TEXT_LENGTH:
        bot.send_message(
            chat_id,
            get_text('text_too_short'),
            parse_mode='Markdown'
        )
        return
    
    # Send processing message
    processing_msg = bot.send_message(
        chat_id,
        get_text('analyzing_text')
    )
    
    # Generate questions
    generate_questions_async(chat_id, text, processing_msg)
    
    # Reset waiting state
    with user_data_lock:
        if chat_id in user_data:
            user_data[chat_id]['waiting_for'] = None

def generate_questions_async(chat_id, text, processing_msg=None):
    """Asynchronous wrapper for generate_questions"""
    def _generate():
        try:
            # Create a copy of text to avoid reference issues
            text_copy = text
            generate_questions(chat_id, text_copy, processing_msg)
            
            # Clean up the text copy
            del text_copy
            gc.collect()
            
        except Exception as e:
            print(f"Error in generate_questions_async: {e}")
            
    executor.submit(_generate)

def generate_questions(chat_id, text, processing_msg=None):
    try:
        # Get user preferences
        with user_data_lock:
            if chat_id not in user_data:
                user_data[chat_id] = {}
            user_info = user_data[chat_id].copy()
        
        model = user_info.get('model', '1')  # Default to model 1
        
        success = False
        result = None
        
        if model == '1':
            # Use model 1
            success, result = api_service1.generate_questions(text)
        else:
            # Use model 2 with question count
            question_count = user_info.get('question_count', 10)  # Default to 10 questions
            success, result = api_service2.generate_questions(text, question_count)
        
        # Clean up text as soon as we're done with it
        del text
        gc.collect()
        
        if success:
            # Handle questions based on model
            if model == '1':
                send_model1_questions(chat_id, result, processing_msg)
            else:
                send_model2_questions(chat_id, result, processing_msg)
                
            # Clean up user data after completing the task
            with user_data_lock:
                if chat_id in user_data:
                    user_data[chat_id] = {}
                    
            # Clean up result
            del result
            gc.collect()
        else:
            bot.send_message(chat_id, f"❌ {result}")
            notify_admin(f"Question generation failed: {result}")
        
    except Exception as e:
        bot.send_message(
            chat_id,
            get_text('error', str(e)),
            parse_mode='Markdown'
        )
        notify_admin(f"Error occurred during question generation: {str(e)}")
        
        bot.send_message(
            chat_id,
            get_text('returning_to_menu'),
            reply_markup=create_main_menu()
        )

def send_model1_questions(chat_id, questions, processing_msg=None):
    if not questions:
        if processing_msg:
            bot.edit_message_text(
                get_text('no_questions'),
                chat_id,
                processing_msg.message_id,
                parse_mode='Markdown'
            )
        return
    
    if processing_msg:
        bot.edit_message_text(
            get_text('questions_generated', len(questions)),
            chat_id,
            processing_msg.message_id
        )
    
    # Track skipped questions
    skipped_questions = 0
    sent_questions = 0
    
    # Send questions
    for i, question in enumerate(questions, 1):
        if isinstance(question, dict):
            question_text = question.get('question', '')
            answers = question.get('answers', [])
            
            # Skip if question text is too long
            if len(question_text) > 300:
                skipped_questions += 1
                continue
            
            # Filter out answers that are too long
            valid_answers = []
            for answer in answers:
                answer_text = answer.get('answer', '')
                if len(answer_text) <= 100:
                    valid_answers.append(answer)
            
            # Skip if we don't have enough valid answers
            if len(valid_answers) < 2:
                skipped_questions += 1
                continue
            
            options = [answer.get('answer', '') for answer in valid_answers]
            correct_option = next((i for i, ans in enumerate(valid_answers) if ans.get('isCorrect', False)), 0)
            
            # Get explanation
            explanation = question.get('explanation', '')
            if explanation and len(explanation) > 200:
                explanation = explanation[:197] + "..."
            
            try:
                bot.send_poll(
                    chat_id,
                    question_text,
                    options=options,
                    is_anonymous=True,
                    type='quiz',
                    correct_option_id=correct_option,
                    explanation=explanation
                )
                sent_questions += 1
            except Exception as e:
                skipped_questions += 1
                continue
    
    # Notify admin about successful generation
    notify_admin(
        f"Model 1 questions generated:\n"
        f"• Total: {len(questions)}\n"
        f"• Sent: {sent_questions}\n"
        f"• Skipped: {skipped_questions}"
    )
    
    # Return to main menu
    bot.send_message(
        chat_id,
        get_text('quiz_completed'),
        parse_mode='Markdown',
        reply_markup=create_main_menu()
    )

def send_model2_questions(chat_id, questions, processing_msg=None):
    if not questions:
        if processing_msg:
            bot.edit_message_text(
                get_text('no_questions'),
                chat_id,
                processing_msg.message_id,
                parse_mode='Markdown'
            )
        return
    
    if processing_msg:
        bot.edit_message_text(
            get_text('questions_generated', len(questions)),
            chat_id,
            processing_msg.message_id
        )
    
    # Track skipped questions
    skipped_questions = 0
    sent_questions = 0
    
    # Send questions
    for i, question_data in questions.items():
        if isinstance(question_data, dict):
            question_text = question_data.get('text', '')
            options_dict = question_data.get('options', {})
            correct_answer = question_data.get('answer', '')
            
            # Skip if question text is too long
            if len(question_text) > 300:
                skipped_questions += 1
                continue
            
            # Check if we have a valid correct answer
            if not correct_answer or not correct_answer.lower() in options_dict:
                skipped_questions += 1
                continue
            
            # Format options and handle shuffling
            formatted_options = [f"{key}) {value}" for key, value in options_dict.items()]
            correct_option_text = f"{correct_answer}) {options_dict[correct_answer]}"
            
            # Shuffle options
            random.shuffle(formatted_options)
            
            # Find correct option index after shuffling
            correct_option_id = -1
            for i, opt in enumerate(formatted_options):
                if opt.startswith(f"{correct_answer})"):
                    correct_option_id = i
                    break
                    
            if correct_option_id < 0:
                skipped_questions += 1
                continue
            
            # Remove the option prefix (e.g., "a) ") before sending
            options = [re.sub(r'^[a-zA-Z]\)\s*', '', opt) for opt in formatted_options]
            
            try:
                bot.send_poll(
                    chat_id,
                    question_text,
                    options=options,
                    is_anonymous=True,
                    type='quiz',
                    correct_option_id=correct_option_id
                )
                sent_questions += 1
            except Exception as e:
                skipped_questions += 1
                continue
    
    # Notify admin about successful generation
    notify_admin(
        f"Model 2 questions generated:\n"
        f"• Total: {len(questions)}\n"
        f"• Sent: {sent_questions}\n"
        f"• Skipped: {skipped_questions}"
    )
    
    # Return to main menu
    bot.send_message(
        chat_id,
        get_text('quiz_completed'),
        parse_mode='Markdown',
        reply_markup=create_main_menu()
    )

# Default message handler
@bot.message_handler(func=lambda message: True)
def default_handler(message):
    chat_id = message.chat.id
    
    # Check if waiting for text
    with user_data_lock:
        if chat_id in user_data and user_data[chat_id].get('waiting_for') == 'text':
            handle_text_input(message)
            return
    
    # Otherwise show main menu
    bot.send_message(
        chat_id,
        get_text('welcome'),
        parse_mode='Markdown',
        reply_markup=create_main_menu()
    )

if __name__ == '__main__':
    print("🤖 Bot is running...")
    keep_alive()
    while True:
        try:
            bot.infinity_polling(timeout=600, long_polling_timeout=600)
        except Exception as e:
            print(f"Bot polling error: {e}")
            continue



