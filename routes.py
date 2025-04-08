import uuid
import json
from flask import render_template, request, jsonify, session, redirect, url_for
from extensions import db
from models import User, Conversation, Message, LanguageError
from services.ai_service import generate_bot_response
from services.tts_service import generate_speech
from services.translation_service import translate_text
from services.error_detector import detect_errors

def register_routes(app):
    @app.route('/', methods=['GET'])
    def index():
        """Render the homepage with language selection form."""
        languages = [
            "English", "Spanish", "French", "German", "Italian", 
            "Portuguese", "Chinese", "Japanese", "Korean", "Russian",
            "Arabic", "Hindi", "Dutch", "Swedish", "Polish", "Turkish"
        ]
        
        proficiency_levels = ["Beginner", "Intermediate", "Advanced"]
        
        return render_template('index.html', 
                               languages=languages,
                               proficiency_levels=proficiency_levels)

    @app.route('/setup', methods=['POST'])
    def setup():
        """Handle the language setup form submission."""
        native_language = request.form.get('native_language')
        target_language = request.form.get('target_language')
        proficiency_level = request.form.get('proficiency_level')
        
        if not all([native_language, target_language, proficiency_level]):
            return jsonify({'error': 'All fields are required'}), 400
        
        # Generate a unique session ID for the user
        session_id = str(uuid.uuid4())
        session['session_id'] = session_id
        
        # Create a new user with the provided preferences
        new_user = User(
            session_id=session_id,
            native_language=native_language,
            target_language=target_language,
            proficiency_level=proficiency_level
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        # Store user ID in session
        session['user_id'] = new_user.id
        
        return redirect(url_for('chat'))

    @app.route('/chat', methods=['GET'])
    def chat():
        """Render the chat interface."""
        if 'user_id' not in session:
            return redirect(url_for('index'))
        
        user_id = session['user_id']
        user = User.query.get(user_id)
        
        if not user:
            return redirect(url_for('index'))
        
        scenarios = [
            {"id": "cafe", "name": "At a Café", "icon": "coffee"},
            {"id": "shopping", "name": "Shopping at a Mall", "icon": "shopping-bag"},
            {"id": "airport", "name": "Traveling at the Airport", "icon": "plane"},
            {"id": "meeting", "name": "Meeting New People", "icon": "users"},
            {"id": "doctor", "name": "Visiting a Doctor", "icon": "activity"}
        ]
        
        return render_template('chat.html', 
                               user=user,
                               scenarios=scenarios)

    @app.route('/api/start_conversation', methods=['POST'])
    def start_conversation():
        """Start a new conversation with the selected scenario."""
        if 'user_id' not in session:
            return jsonify({'error': 'User not found'}), 401
        
        user_id = session['user_id']
        scenario = request.json.get('scenario')
        
        if not scenario:
            return jsonify({'error': 'Scenario is required'}), 400
        
        # Create a new conversation
        conversation = Conversation(
            user_id=user_id,
            scenario=scenario
        )
        
        db.session.add(conversation)
        db.session.commit()
        
        # Get user information for context
        user = User.query.get(user_id)
        
        # Generate initial bot message based on scenario
        response, translated = generate_bot_response(
            None, 
            scenario, 
            user.target_language, 
            user.native_language,
            user.proficiency_level,
            is_initial=True
        )
        
        # Save bot message to database
        bot_message = Message(
            conversation_id=conversation.id,
            is_user=False,
            content=response,
            translated_content=translated
        )
        
        db.session.add(bot_message)
        db.session.commit()
        
        # Store conversation ID in session
        session['conversation_id'] = conversation.id
        
        return jsonify({
            'conversation_id': conversation.id,
            'message': {
                'id': bot_message.id,
                'content': bot_message.content,
                'translated': bot_message.translated_content,
                'is_user': bot_message.is_user,
                'timestamp': bot_message.timestamp.isoformat()
            }
        })

    @app.route('/api/send_message', methods=['POST'])
    def send_message():
        """Process a user message and generate a bot response."""
        if 'user_id' not in session or 'conversation_id' not in session:
            return jsonify({'error': 'Session data not found'}), 401
        
        user_id = session['user_id']
        conversation_id = session['conversation_id']
        
        message_content = request.json.get('message')
        
        if not message_content:
            return jsonify({'error': 'Message content is required'}), 400
        
        # Get user and conversation info
        user = User.query.get(user_id)
        conversation = Conversation.query.get(conversation_id)
        
        if not user or not conversation:
            return jsonify({'error': 'User or conversation not found'}), 404
            
        # Save user message
        user_message = Message(
            conversation_id=conversation_id,
            is_user=True,
            content=message_content
        )
        
        db.session.add(user_message)
        db.session.commit()
        
        # Detect language errors in the user's message
        errors = detect_errors(
            message_content, 
            user.target_language, 
            user.proficiency_level
        )
        
        # Save detected errors
        error_data = []
        for error in errors:
            language_error = LanguageError(
                user_id=user_id,
                conversation_id=conversation_id,
                message_id=user_message.id,
                error_text=error['error_text'],
                correction=error['correction'],
                error_type=error['error_type']
            )
            db.session.add(language_error)
            error_data.append({
                'error_text': error['error_text'],
                'correction': error['correction'],
                'error_type': error['error_type']
            })
        
        db.session.commit()
        
        # Generate bot response
        response, translated = generate_bot_response(
            message_content,
            conversation.scenario,
            user.target_language,
            user.native_language,
            user.proficiency_level
        )
        
        # Save bot response
        bot_message = Message(
            conversation_id=conversation_id,
            is_user=False,
            content=response,
            translated_content=translated
        )
        
        db.session.add(bot_message)
        db.session.commit()
        
        return jsonify({
            'user_message': {
                'id': user_message.id,
                'content': user_message.content,
                'is_user': True,
                'timestamp': user_message.timestamp.isoformat(),
                'errors': error_data
            },
            'bot_message': {
                'id': bot_message.id,
                'content': bot_message.content,
                'translated': bot_message.translated_content,
                'is_user': False,
                'timestamp': bot_message.timestamp.isoformat()
            }
        })

    @app.route('/api/get_tts', methods=['POST'])
    def get_tts():
        """Generate text-to-speech for a message."""
        message_id = request.json.get('message_id')
        
        if not message_id:
            return jsonify({'error': 'Message ID is required'}), 400
        
        # Get the message
        message = Message.query.get(message_id)
        
        if not message:
            return jsonify({'error': 'Message not found'}), 404
        
        # Get the user's target language
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'User not found'}), 401
            
        user = User.query.get(user_id)
        
        # Generate speech audio
        speech_data = generate_speech(message.content, user.target_language)
        
        return jsonify({
            'audio_data': speech_data
        })

    @app.route('/api/review', methods=['GET'])
    def get_review():
        """Get a review of the conversation, including error summary."""
        if 'user_id' not in session or 'conversation_id' not in session:
            return jsonify({'error': 'Session data not found'}), 401
        
        user_id = session['user_id']
        conversation_id = session['conversation_id']
        
        # Get all errors for this conversation
        errors = LanguageError.query.filter_by(
            user_id=user_id,
            conversation_id=conversation_id
        ).all()
        
        # Group errors by type
        error_summary = {}
        for error in errors:
            if error.error_type not in error_summary:
                error_summary[error.error_type] = []
                
            error_summary[error.error_type].append({
                'error_text': error.error_text,
                'correction': error.correction
            })
        
        # Generate improvement suggestions
        suggestions = []
        
        # Count errors by type for targeted suggestions
        if 'grammar' in error_summary and len(error_summary['grammar']) >= 2:
            suggestions.append("Focus on improving your grammar skills, particularly with sentence structure.")
            
        if 'vocabulary' in error_summary and len(error_summary['vocabulary']) >= 2:
            suggestions.append("Work on expanding your vocabulary in this context.")
            
        if 'syntax' in error_summary and len(error_summary['syntax']) >= 2:
            suggestions.append("Pay attention to word order and syntax rules.")
        
        # If few errors, provide positive reinforcement
        if len(errors) < 3:
            suggestions.append("Great job! You made very few mistakes in this conversation.")
        
        # Add a generic suggestion if no specific ones were generated
        if not suggestions:
            suggestions.append("Continue practicing in different scenarios to improve your language skills.")
        
        return jsonify({
            'error_summary': error_summary,
            'suggestions': suggestions,
            'total_errors': len(errors)
        })

    @app.route('/api/history', methods=['GET'])
    def get_history():
        """Get the conversation history."""
        if 'conversation_id' not in session:
            return jsonify({'error': 'No active conversation'}), 401
            
        conversation_id = session['conversation_id']
        
        # Get all messages for this conversation
        messages = Message.query.filter_by(
            conversation_id=conversation_id
        ).order_by(Message.timestamp).all()
        
        # Get all errors for user messages
        error_map = {}
        for message in messages:
            if message.is_user:
                errors = LanguageError.query.filter_by(message_id=message.id).all()
                if errors:
                    error_map[message.id] = [{
                        'error_text': error.error_text,
                        'correction': error.correction,
                        'error_type': error.error_type
                    } for error in errors]
        
        # Format messages for the response
        message_history = []
        for message in messages:
            message_data = {
                'id': message.id,
                'content': message.content,
                'translated': message.translated_content,
                'is_user': message.is_user,
                'timestamp': message.timestamp.isoformat()
            }
            
            # Add errors if this is a user message with errors
            if message.id in error_map:
                message_data['errors'] = error_map[message.id]
                
            message_history.append(message_data)
        
        return jsonify({
            'messages': message_history
        })
