import os
import base64
import tempfile
from gtts import gTTS
import logging

logger = logging.getLogger(__name__)

def generate_speech(text, language_code):
    """
    Generate speech audio for the given text in the specified language.
    
    Args:
        text (str): The text to convert to speech
        language_code (str): The language code for the text
        
    Returns:
        str: Base64-encoded audio data
    """
    try:
        # Map language names to gTTS language codes
        language_map = {
            "English": "en",
            "Spanish": "es",
            "French": "fr",
            "German": "de",
            "Italian": "it",
            "Portuguese": "pt",
            "Chinese": "zh-CN",
            "Japanese": "ja",
            "Korean": "ko",
            "Russian": "ru",
            "Arabic": "ar",
            "Hindi": "hi",
            "Dutch": "nl",
            "Swedish": "sv",
            "Polish": "pl",
            "Turkish": "tr"
        }
        
        # Get the appropriate language code
        tts_lang = language_map.get(language_code, "en")
        
        # Create temporary file for audio
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
            temp_filename = temp_file.name
            
        # Generate speech
        tts = gTTS(text=text, lang=tts_lang, slow=False)
        tts.save(temp_filename)
        
        # Read the file and encode to base64
        with open(temp_filename, "rb") as audio_file:
            audio_data = audio_file.read()
            encoded_audio = base64.b64encode(audio_data).decode('utf-8')
            
        # Clean up temporary file
        os.unlink(temp_filename)
        
        return encoded_audio
        
    except Exception as e:
        logger.error(f"Error generating speech: {str(e)}")
        return None
