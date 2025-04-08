import logging
import json
from flask import current_app
import requests

logger = logging.getLogger(__name__)

def translate_text(text, source_language, target_language):
    """
    Translate text from source language to target language using OpenRouter API with Google Gemini model.
    
    Args:
        text (str): The text to translate
        source_language (str): The language of the original text
        target_language (str): The language to translate to
        
    Returns:
        str: The translated text
    """
    # Use OpenRouter API key for translation
    api_key = current_app.config.get('OPENROUTER_API_KEY')
    
    if not api_key:
        logger.warning("OpenRouter API key not found, using mock translation")
        return f"[Translation to {target_language}]: {text}"
    
    try:
        # Create a translation prompt
        translation_prompt = f"""Translate the following text from {source_language} to {target_language}:

Text to translate: "{text}"

Translation:"""
        
        # Get the model from the config or use the default one
        model = current_app.config.get('OPENROUTER_MODEL', 'google/gemini-2.5-pro-exp-03-25:free')
        
        # Prepare the request data
        request_data = {
            "model": model,
            "messages": [
                {"role": "system", "content": f"You are a professional translator. Translate the given text from {source_language} to {target_language} accurately. Respond with only the translated text, no commentary."},
                {"role": "user", "content": translation_prompt}
            ]
        }
        
        # Make the API request directly with requests
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
                "HTTP-Referer": "https://linguabot.replit.app",
                "X-Title": "LinguaBot Language Learning Assistant"
            },
            json=request_data
        )
        
        # Check if the request was successful
        if response.status_code == 200:
            # Parse the response JSON
            response_data = response.json()
            
            # Log the complete response for debugging
            logger.debug(f"OpenRouter translation response: {json.dumps(response_data, indent=2)}")
            
            # Extract the translation
            if 'choices' in response_data and len(response_data['choices']) > 0:
                if 'message' in response_data['choices'][0] and 'content' in response_data['choices'][0]['message']:
                    translation = response_data['choices'][0]['message']['content'].strip()
                    
                    # Clean up quotation marks if the model included them
                    translation = translation.strip('"')
                    
                    return translation
                else:
                    logger.error(f"Missing message content in response: {response_data}")
                    return f"[Translation error: Unexpected response format]"
            else:
                logger.error(f"Missing choices in response: {response_data}")
                return f"[Translation error: No translation provided]"
        else:
            logger.error(f"OpenRouter API error: {response.status_code} - {response.text}")
            return f"[Translation error: API status {response.status_code}]"
        
    except Exception as e:
        logger.error(f"Error in translation service: {str(e)}")
        return f"[Translation error: {str(e)}]"
