from datetime import datetime
from app import db

class User(db.Model):
    """User model for storing user preferences and settings."""
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(64), unique=True, nullable=False)
    native_language = db.Column(db.String(50), nullable=False)
    target_language = db.Column(db.String(50), nullable=False)
    proficiency_level = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    conversations = db.relationship('Conversation', backref='user', lazy=True)
    language_errors = db.relationship('LanguageError', backref='user', lazy=True)
    
    def __repr__(self):
        return f'<User {self.id}: {self.native_language} -> {self.target_language}>'


class Conversation(db.Model):
    """Model for storing conversation data."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    scenario = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    messages = db.relationship('Message', backref='conversation', lazy=True)
    
    def __repr__(self):
        return f'<Conversation {self.id}: {self.scenario}>'


class Message(db.Model):
    """Model for storing individual messages in a conversation."""
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversation.id'), nullable=False)
    is_user = db.Column(db.Boolean, default=False)  # True if user message, False if bot message
    content = db.Column(db.Text, nullable=False)
    translated_content = db.Column(db.Text, nullable=True)  # For storing translations
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        sender = "User" if self.is_user else "Bot"
        return f'<Message {self.id} from {sender}: {self.content[:20]}...>'


class LanguageError(db.Model):
    """Model for tracking language errors and corrections."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversation.id'), nullable=False)
    message_id = db.Column(db.Integer, db.ForeignKey('message.id'), nullable=False)
    error_text = db.Column(db.Text, nullable=False)
    correction = db.Column(db.Text, nullable=False)
    error_type = db.Column(db.String(50), nullable=False)  # e.g., grammar, vocabulary, syntax
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    conversation = db.relationship('Conversation', backref='errors')
    message = db.relationship('Message', backref='errors')
    
    def __repr__(self):
        return f'<Error {self.id}: {self.error_type} - {self.error_text[:20]}...>'
