import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("python-dotenv not found, using environment variables directly")

# Web App Configuration
SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')

# Minimum text length required for generating questions
MIN_TEXT_LENGTH = int(os.getenv('MIN_TEXT_LENGTH', '30'))

# Maximum file size for PDF uploads (in bytes)
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

# Allowed file extensions
ALLOWED_EXTENSIONS = {'pdf'}

# Message Templates for Web App
MESSAGES = {
    'en': {
        'welcome': "Welcome to RefOo Quiz Maker!",
        'model_selection': "Choose your quiz creator",
        'question_count': "How many questions would you like?",
        'input_method': "How would you like to share your materials?",
        'send_text': "Paste your study text",
        'send_pdf': "Upload PDF document",
        'processing': "Processing your request...",
        'generating': "Generating questions...",
        'quiz_ready': "Your quiz is ready!",
        'no_questions': "No questions could be generated from this material.",
        'text_too_short': "Text is too short. Please provide more content.",
        'invalid_pdf': "Please upload a valid PDF file.",
        'invalid_range': "Please specify a valid page range.",
        'error': "Something went wrong. Please try again.",
        'contact': "Need help? Contact us at raafatsami101@gmail.com"
    }
}

# Question Count Options
QUESTION_COUNTS = {
    'en': {
        '5': '5 Questions',
        '10': '10 Questions',
        '15': '15 Questions',
        '20': '20 Questions',
        '25': '25 Questions',
        '30': '30 Questions'
    }
}
