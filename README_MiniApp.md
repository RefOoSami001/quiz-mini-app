# RefOo Quiz Maker - Telegram Mini App

A Telegram Mini App that transforms study materials into interactive quizzes. This web-based application provides the same functionality as the original Telegram bot but with a modern, responsive interface.

## Features

- **Interactive Web Interface**: Modern, responsive design optimized for mobile devices
- **Dual AI Models**:
  - Standard Quiz (with explanations)
  - Custom Quiz (choose question count)
- **Multiple Input Methods**:
  - Text input for direct content
  - PDF upload with page range selection
- **Real-time Processing**: Asynchronous question generation with progress indicators
- **Interactive Quiz Experience**: Navigate through questions with immediate feedback
- **Results Tracking**: Score calculation and performance feedback
- **Telegram Integration**: Native Telegram WebApp API integration

## Architecture

### Frontend

- **HTML/CSS/JavaScript**: Responsive web interface
- **Telegram WebApp API**: Native Telegram integration
- **Progressive Enhancement**: Works on all modern browsers

### Backend

- **Flask**: Lightweight Python web framework
- **Asynchronous Processing**: Thread pool for question generation
- **Session Management**: User session handling
- **API Integration**: Connects to existing MCQ generation services

## Setup

### Prerequisites

- Python 3.7+
- Flask
- Access to the existing API services

### Installation

1. **Install Dependencies**:

```bash
pip install -r requirements_web.txt
```

2. **Environment Configuration**:
   Create a `.env` file:

```
SECRET_KEY=your-secret-key-here
MIN_TEXT_LENGTH=30
```

3. **Run the Application**:

```bash
python app.py
```

The app will be available at `http://localhost:5000`

### Deployment

#### Heroku Deployment

1. **Rename Files**:

   - Rename `Procfile_web` to `Procfile`
   - Rename `requirements_web.txt` to `requirements.txt`

2. **Deploy**:

```bash
git add .
git commit -m "Deploy Telegram Mini App"
git push heroku main
```

#### Other Platforms

The app can be deployed to any platform that supports Flask applications:

- Railway
- Render
- DigitalOcean App Platform
- AWS Elastic Beanstalk

## Telegram Mini App Setup

### 1. Create Bot

1. Message [@BotFather](https://t.me/botfather) on Telegram
2. Create a new bot with `/newbot`
3. Get your bot token

### 2. Configure Mini App

1. Use `/newapp` command with BotFather
2. Provide your deployed web app URL
3. Set up the mini app parameters

### 3. Web App Configuration

The app automatically integrates with Telegram's WebApp API:

- Uses Telegram theme colors
- Supports Telegram's native UI elements
- Handles Telegram user data
- Provides native sharing capabilities

## API Endpoints

### Core Endpoints

- `POST /api/generate-questions` - Generate questions from text
- `POST /api/check-generation-status` - Check generation progress
- `POST /api/process-pdf` - Process PDF files
- `POST /api/get-session-data` - Retrieve session data
- `POST /api/clear-session` - Clear user session

### Request/Response Format

All API endpoints use JSON format:

```json
{
  "success": true/false,
  "data": {...},
  "error": "error message"
}
```

## File Structure

```
├── app.py                 # Main Flask application
├── templates/
│   └── index.html        # Main web interface
├── config_web.py         # Web app configuration
├── requirements_web.txt  # Python dependencies
├── Procfile_web         # Deployment configuration
├── api_service.py        # Existing API service 1
├── api_service2.py       # Existing API service 2
└── README_MiniApp.md     # This file
```

## Key Features Implementation

### 1. Model Selection

- Two AI models with different capabilities
- Visual selection interface
- Conditional flow based on model choice

### 2. PDF Processing

- File upload with validation
- Page range selection
- Text extraction with progress indication
- Error handling for invalid files

### 3. Question Generation

- Asynchronous processing
- Real-time status updates
- Error handling and user feedback
- Session management

### 4. Interactive Quiz

- Question navigation
- Answer selection
- Progress tracking
- Results calculation

### 5. Responsive Design

- Mobile-first approach
- Telegram theme integration
- Touch-friendly interface
- Cross-platform compatibility

## Customization

### Styling

The app uses CSS custom properties that automatically adapt to Telegram's theme:

- `--tg-theme-bg-color`: Background color
- `--tg-theme-text-color`: Text color
- `--tg-theme-button-color`: Button color
- `--tg-theme-secondary-bg-color`: Secondary background

### Configuration

Modify `config_web.py` to:

- Change minimum text length
- Update message templates
- Modify question count options
- Adjust file size limits

## Troubleshooting

### Common Issues

1. **PDF Processing Errors**:

   - Ensure PDF is not password-protected
   - Check file size limits
   - Verify page range format

2. **Question Generation Failures**:

   - Check API service availability
   - Verify text length requirements
   - Monitor session storage

3. **Telegram Integration Issues**:
   - Verify bot token configuration
   - Check WebApp URL settings
   - Ensure HTTPS deployment

### Debug Mode

Enable debug mode for development:

```python
app.run(debug=True)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project maintains the same license as the original bot.

## Support

For support and questions:

- Email: raafatsami101@gmail.com
- Telegram: @RefOoSami
- WhatsApp: +201011508719
