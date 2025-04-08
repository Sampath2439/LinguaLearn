import os
import json
import requests
import logging
from flask import current_app
from services.translation_service import translate_text

logger = logging.getLogger(__name__)

def generate_bot_response(user_message, scenario, target_language, native_language, proficiency_level, is_initial=False):
    """
    Generate a response from the AI chatbot based on the user's message and scenario.
    
    Args:
        user_message (str): The message from the user, or None if this is the initial message
        scenario (str): The conversation scenario (e.g., "cafe", "shopping")
        target_language (str): The language the user is learning
        native_language (str): The user's native language
        proficiency_level (str): The user's proficiency level (Beginner, Intermediate, Advanced)
        is_initial (bool): Whether this is the initial message in the conversation
        
    Returns:
        tuple: (response_text, translated_text)
    """
    api_key = current_app.config.get('OPENROUTER_API_KEY')
    if not api_key:
        logger.error("OpenRouter API key is not set")
        return "I'm sorry, I can't generate a response right now. API key is missing.", "Error: API key missing"
    
    # Define scenario descriptions
    scenario_descriptions = {
        "cafe": "a conversation in a café where the user is ordering food and drinks",
        "shopping": "a conversation in a shopping mall where the user is looking for clothes or other items",
        "airport": "a conversation at an airport where the user is navigating check-in, security, and finding their gate",
        "meeting": "a conversation where the user is meeting new people and introducing themselves",
        "doctor": "a conversation at a doctor's office where the user is describing symptoms and receiving advice"
    }
    
    scenario_desc = scenario_descriptions.get(scenario, f"a conversation related to {scenario}")
    
    # Define proficiency level descriptions
    level_descriptions = {
        "Beginner": "Keep sentences short and simple. Use basic vocabulary and grammar.",
        "Intermediate": "Use moderate complexity sentences. Introduce some idiomatic expressions.",
        "Advanced": "Use natural, complex language with sophisticated vocabulary and grammar."
    }
    
    level_desc = level_descriptions.get(proficiency_level, "Use language appropriate for an average speaker")
    
    # Create system prompt
    system_prompt = f"""You are a language learning assistant helping someone practice {target_language}.
You are simulating {scenario_desc}.

GUIDELINES:
1. Respond ONLY in {target_language}.
2. {level_desc}
3. Keep the conversation relevant to the {scenario} scenario.
4. Be patient, encouraging, and helpful.
5. Your response should be 1-3 sentences long.
6. Do not provide translations or language explanations in your response.
"""

    # Create prompt based on whether this is the initial message
    if is_initial:
        user_prompt = f"Start a conversation with me in {target_language} for the {scenario} scenario. I am a {proficiency_level.lower()} level speaker."
    else:
        user_prompt = user_message
    
    # Prepare request to OpenRouter API
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": current_app.config.get('OPENROUTER_MODEL', 'google/gemini-pro-1.5-experimental'),
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    }
    
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code != 200:
            logger.error(f"API error: {response.status_code} - {response.text}")
            return f"I'm sorry, I encountered an error (status {response.status_code}).", "Error with API response"
        
        response_data = response.json()
        bot_message = response_data['choices'][0]['message']['content'].strip()
        
        # Translate the bot message to the user's native language
        translated_text = translate_text(bot_message, target_language, native_language)
        
        return bot_message, translated_text
        
    except Exception as e:
        logger.error(f"Error generating bot response: {str(e)}")
        return "I'm sorry, I encountered an error while generating a response.", "Error occurred"
