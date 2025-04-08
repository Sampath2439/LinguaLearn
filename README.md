# LinguaBot: AI-Powered Language Learning Assistant

LinguaBot is an interactive language learning application that helps users practice conversations in different languages through scenario-based interactions with an AI language assistant.

## Features

- Interactive conversations in various realistic scenarios (cafe, shopping, airport, etc.)
- Real-time language feedback and error detection
- Text-to-speech functionality for pronunciation practice
- Performance review with error summary and improvement suggestions
- Support for multiple languages and proficiency levels

## Technology Stack

- **Backend**: Flask, SQLAlchemy
- **Frontend**: HTML/CSS/JavaScript
- **AI/ML**: OpenRouter API (Google Gemini 2.5 Pro)
- **Text-to-Speech**: gTTS (Google Text-to-Speech)
- **Database**: SQLite (development), PostgreSQL (production)

## Deployment to Vercel

This project is configured for deployment on Vercel. Follow these steps to deploy:

1. Install the Vercel CLI:
   ```
   npm install -g vercel
   ```

2. Log in to Vercel:
   ```
   vercel login
   ```

3. Deploy the project:
   ```
   vercel
   ```

4. Set up environment variables in the Vercel dashboard:
   - `OPENROUTER_API_KEY`: Your OpenRouter API key
   - `SESSION_SECRET`: A secret key for session management
   - `DATABASE_URL`: (Optional) PostgreSQL database URL if using a database

## Local Development

1. Clone the repository:
   ```
   git clone <repository-url>
   ```

2. Install dependencies:
   ```
   pip install -r requirements-vercel.txt
   ```

3. Run the development server:
   ```
   python main.py
   ```
