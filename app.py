import os
import logging

from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

from extensions import db

from dotenv import load_dotenv
load_dotenv()


# Configure logging with more verbose format
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev_secret_key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)  # needed for url_for to generate with https

# Configure database - Using SQLite for development, but will use PostgreSQL in Vercel production
db_url = os.environ.get("DATABASE_URL", "sqlite:///language_bot.db")

# Handle PostgreSQL format from Vercel/Heroku which starts with postgres://
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = db_url
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize the database with the app
db.init_app(app)

# OpenRouter API configuration - used for both chatbot and translation functionality
app.config["OPENROUTER_API_KEY"] = os.environ.get("OPENROUTER_API_KEY", "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")
app.config["OPENROUTER_MODEL"] = "google/gemini-2.0-flash-exp:free"

with app.app_context():
    # Import models to ensure they're registered with SQLAlchemy
    import models  # noqa: F401
    
    # Create all tables
    db.create_all()
    
    # Import and register routes
    from routes import register_routes
    register_routes(app)
