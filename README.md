# MCQ Generator Telegram Bot

This Telegram bot helps users generate multiple-choice questions from their study materials. It supports both text input and PDF files.

## Features

- Generate MCQ questions from text or PDF files
- Support for PDF page range selection
- Interactive menu system
- Contact developer option
- Poll-based question delivery

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file in the project root and add your Telegram bot token:
```
BOT_TOKEN=your_telegram_bot_token_here
```

3. Run the bot:
```bash
python app.py
```

## Usage

1. Start the bot by sending `/start`
2. Choose between "Create MCQ Questions" or "Contact Developer"
3. If creating MCQ questions:
   - Choose between sending text or PDF
   - For text: Send your study material directly
   - For PDF: Send the PDF file and specify the page range
4. The bot will generate questions and send them as polls

## Requirements

- Python 3.7+
- pyTelegramBotAPI
- pdfplumber
- requests
- python-dotenv

## Note

Make sure to replace the contact information in the code with your actual contact details before deploying. 