import requests
import logging
from flask import current_app

logger = logging.getLogger(__name__)

def translate_text(text, source_language, target_language):
    """
    Translate text from source language to target language using Google Translate API.
    
    Args:
        text (str): The text to translate
        source_language (str): The language of the original text
        target_language (str): The language to translate to
        
    Returns:
        str: The translated text
    """
    # Get API key from config
    api_key = current_app.config.get('GOOGLE_TRANSLATE_API_KEY')
    
    # Map language names to ISO codes for Google Translate API
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
    
    source_code = language_map.get(source_language, "auto")
    target_code = language_map.get(target_language, "en")
    
    # If we don't have an API key, use a simplified approach
    if not api_key:
        logger.warning("Google Translate API key not found, using mock translation")
        return f"[Translation to {target_language}]: {text}"
    
    try:
        # Using Google Translate API v2
        url = f"https://translation.googleapis.com/language/translate/v2"
        
        # Prepare the request parameters
        params = {
            "key": api_key,
            "q": text,
            "target": target_code,
        }
        
        # Add source language if it's not 'auto'
        if source_code != "auto":
            params["source"] = source_code
            
        # Make the API request
        response = requests.post(url, params=params)
        
        # Check if the request was successful
        if response.status_code == 200:
            result = response.json()
            translation = result["data"]["translations"][0]["translatedText"]
            return translation
        else:
            logger.error(f"Google Translate API error: {response.status_code} - {response.text}")
            return f"[Translation error: {response.status_code}]"
    
    except Exception as e:
        logger.error(f"Error in translation service: {str(e)}")
        return f"[Translation error: {str(e)}]"
