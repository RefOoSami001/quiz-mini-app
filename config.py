import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("python-dotenv not found, using environment variables directly")

# Bot Configuration
BOT_TOKEN = os.getenv('BOT_TOKEN', '6982141096:AAEeYdFOuNzLjwZjdgSu2Z3fz9wY5dRXU8I')

# Admin chat ID for notifications
ADMIN_CHAT_ID = int(os.getenv('ADMIN_CHAT_ID', '854578633'))

# Minimum text length required for generating questions
MIN_TEXT_LENGTH = int(os.getenv('MIN_TEXT_LENGTH', '30'))

# Difficulty Levels
DIFFICULTY_LEVELS = {
    'en': {
        'easy': '🟢 Easy',
        'medium': '🟡 Medium',
        'hard': '🔴 Hard',
        'all': '🌈 All Levels'
    },
    'ar': {
        'easy': '🟢 سهل',
        'medium': '🟡 متوسط',
        'hard': '🔴 صعب',
        'all': '🌈 جميع المستويات'
    }
}

# Difficulty Emojis
DIFFICULTY_EMOJIS = {
    'EASY': '🟢',
    'MEDIUM': '🟡',
    'HARD': '🔴',
    'UNKNOWN': '⚪'
}

# Question Count Options
QUESTION_COUNTS = {
    'en': {
        '5': '5 Questions',
        '10': '10 Questions',
        '15': '15 Questions',
        '20': '20 Questions',
        '25': '25 Questions',
        '30': '30 Questions',
        '40': '40 Questions'
    },
    'ar': {
        '5': '5 أسئلة',
        '10': '10 أسئلة',
        '15': '15 سؤال',
        '20': '20 سؤال',
        '25': '25 سؤال',
        '30': '30 سؤال',
        '40': '40 سؤال'
    }
}

# Message Templates
MESSAGES = {
    'en': {
        'welcome': (
            "👋 *Welcome to RefOo Quiz Maker!*\n\n"
            "I can transform your study materials into interactive quizzes. Choose an option to get started!"
        ),
        'help': (
            "❓ *Quick Guide*\n\n"
            "1️⃣ Select 'Create MCQ Questions'\n"
            "2️⃣ Choose a model (Model 2 lets you pick question count)\n"
            "3️⃣ Send text or PDF\n"
            "4️⃣ Get your quiz!\n\n"
            "💡 *Tips:*\n"
            "• Clear, structured text works best\n"
            "• For PDFs, select specific pages for focused quizzes"
        ),
        'contact': (
            "👨‍💻 *Need help?*\n\n"
            "Email: raafatsami101@gmail.com\n"
            "Telegram: @RefOoSami\n"
            "WhatsApp: +201011508719"
        ),
        'model_selection': (
            "🤖 *Choose your quiz creator*\n\n"
            "• *🧠Standard Quiz*: Standard with explanations\n"
            "• *✨Custom Quiz*: Custom number of questions"
        ),
        'question_count': "📊 *How many questions would you like?*",
        'input_method': (
            "📝 *How would you like to share your materials?*\n\n"
            "• 📄 Text message\n"
            "• 📚 PDF document"
        ),
        'send_text': "📝 Now paste or type your study text. The more detailed your text, the better the questions!",
        'text_too_short': "⚠️ I need more information to create good questions. Please send a longer piece of text.",
        'send_pdf': "📚 Please upload your PDF document.",
        'processing_pdf': "⏳ Analyzing your PDF...",
        'extracting_text': "⏳ Creating questions based on your selected pages...",
        'text_extracted': "✅ Content extracted! Building your quiz...",
        'analyzing_text': "🧠 Analyzing your material and crafting questions...",
        'no_questions': (
            "⚠️ I couldn't generate questions from this material.\n\n"
            "Try sharing different content or more detailed information."
        ),
        'questions_generated': "✨ Your quiz is ready! Sending {0} questions...",
        'invalid_pdf': "⚠️ Please send a valid PDF file.",
        'pdf_error': "⚠️ I had trouble reading that PDF. Could you try another file?",
        'invalid_range': "⚠️ Please use the format '1-10' to specify page numbers.",
        'error': "⚠️ Something went wrong. Let's try again!",
        'returning_to_menu': "Taking you back to the main menu...",
        'main_menu': "*What would you like to do?*",
        'create_mcq': "📝 Create Quiz",
        'contact_dev': "👨‍💻 Contact Support",
        'help_btn': "❓ How to Use",
        'model1': "🧠 Standard Quiz",
        'model2': "✨ Custom Quiz",
        'text_btn': "📄 Text",
        'pdf_btn': "📚 PDF",
        'quiz_completed': "🎉 *Your quiz is complete!*\n\nWould you like to create another one?"
    },
    'ar': {
        'welcome': (
            "👋 *مرحباً بك في كويز جين!*\n\n"
            "يمكنني تحويل موادك الدراسية إلى اختبارات تفاعلية. اختر خياراً للبدء!"
        ),
        'help': (
            "❓ *دليل سريع*\n\n"
            "1️⃣ اختر 'إنشاء أسئلة اختيار من متعدد'\n"
            "2️⃣ اختر نموذجاً (النموذج 2 يتيح لك اختيار عدد الأسئلة)\n"
            "3️⃣ أرسل نص أو ملف PDF\n"
            "4️⃣ احصل على اختبارك!\n\n"
            "💡 *نصائح:*\n"
            "• النص الواضح والمنظم يعمل بشكل أفضل\n"
            "• بالنسبة لملفات PDF، اختر صفحات محددة للاختبارات المركزة"
        ),
        'contact': (
            "👨‍💻 *بحاجة إلى مساعدة؟*\n\n"
            "البريد الإلكتروني: raafatsami101@gmail.com\n"
            "تليجرام: @RefOoSami\n"
            "واتساب: +201011508719"
        ),
        'model_selection': (
            "🤖 *اختر منشئ الاختبار الخاص بك*\n\n"
            "• *النموذج 1*: قياسي مع شروحات\n"
            "• *النموذج 2*: عدد مخصص من الأسئلة"
        ),
        'question_count': "📊 *كم عدد الأسئلة التي ترغب فيها؟*",
        'input_method': (
            "📝 *كيف تود مشاركة موادك؟*\n\n"
            "• 📄 رسالة نصية\n"
            "• 📚 ملف PDF"
        ),
        'send_text': "📝 الآن انسخ أو اكتب نص الدراسة. كلما كان النص أكثر تفصيلاً، كانت الأسئلة أفضل!",
        'text_too_short': "⚠️ أحتاج إلى مزيد من المعلومات لإنشاء أسئلة جيدة. يرجى إرسال نص أطول.",
        'send_pdf': "📚 يرجى تحميل ملف PDF الخاص بك.",
        'processing_pdf': "⏳ تحليل ملف PDF الخاص بك...",
        'extracting_text': "⏳ إنشاء أسئلة بناءً على الصفحات المختارة...",
        'text_extracted': "✅ تم استخراج المحتوى! بناء اختبارك...",
        'analyzing_text': "🧠 تحليل المواد الخاصة بك وصياغة الأسئلة...",
        'no_questions': (
            "⚠️ لم أتمكن من إنشاء أسئلة من هذه المادة.\n\n"
            "حاول مشاركة محتوى مختلف أو معلومات أكثر تفصيلاً."
        ),
        'questions_generated': "✨ اختبارك جاهز! إرسال {0} أسئلة...",
        'invalid_pdf': "⚠️ يرجى إرسال ملف PDF صالح.",
        'pdf_error': "⚠️ واجهت صعوبة في قراءة ملف PDF هذا. هل يمكنك تجربة ملف آخر؟",
        'invalid_range': "⚠️ يرجى استخدام التنسيق '1-10' لتحديد أرقام الصفحات.",
        'error': "⚠️ حدث خطأ ما. دعنا نحاول مرة أخرى!",
        'returning_to_menu': "إعادتك إلى القائمة الرئيسية...",
        'main_menu': "*ماذا تريد أن تفعل؟*",
        'create_mcq': "📝 إنشاء اختبار",
        'contact_dev': "👨‍💻 اتصل بالدعم",
        'help_btn': "❓ كيفية الاستخدام",
        'model1': "🧠 اختبار قياسي",
        'model2': "✨ اختبار مخصص",
        'text_btn': "📄 نص",
        'pdf_btn': "📚 PDF",
        'quiz_completed': "🎉 *اكتمل اختبارك!*\n\nهل ترغب في إنشاء اختبار آخر؟"
    }
} 