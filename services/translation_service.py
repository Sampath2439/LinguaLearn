import logging
from flask import current_app
from openai import OpenAI

logger = logging.getLogger(__name__)

def translate_text(text, source_language, target_language):
    """
    Translate text from source language to target language.
    
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
    
    # Initialize OpenAI client with OpenRouter endpoint
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key
    )
    
    try:
        # Create a translation prompt
        translation_prompt = f"""Translate the following text from {source_language} to {target_language}:

Text to translate: "{text}"

Translation:"""

        # Get the model from the config or use the default one
        model = current_app.config.get('OPENROUTER_MODEL', 'google/gemini-2.5-pro-exp-03-25:free')
        
        # Make the API request using the OpenAI client
        completion = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": "https://linguabot.replit.app", 
                "X-Title": "LinguaBot Language Learning Assistant",
            },
            model=model,
            messages=[
                {"role": "system", "content": f"You are a professional translator. Translate the given text from {source_language} to {target_language} accurately."},
                {"role": "user", "content": translation_prompt}
            ]
        )
        
        translation = completion.choices[0].message.content.strip()
        
        # Clean up quotation marks if the model included them
        translation = translation.strip('"')
        
        return translation
        
    except Exception as e:
        logger.error(f"Error in translation service: {str(e)}")
        return f"[Translation error: {str(e)}]"
