import os
import logging

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix


class Base(DeclarativeBase):
    pass


# Configure logging with more verbose format
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Initialize SQLAlchemy
db = SQLAlchemy(model_class=Base)

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
app.config["OPENROUTER_API_KEY"] = os.environ.get("OPENROUTER_API_KEY", "")
app.config["OPENROUTER_MODEL"] = "google/gemini-2.5-pro-exp-03-25:free"

with app.app_context():
    # Import models to ensure they're registered with SQLAlchemy
    import models  # noqa: F401
    
    # Create all tables
    db.create_all()
    
    # Import and register routes
    from routes import register_routes
    register_routes(app)
