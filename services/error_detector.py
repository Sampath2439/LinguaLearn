import requests
import logging
from flask import current_app

logger = logging.getLogger(__name__)

def detect_errors(message, target_language, proficiency_level):
    """
    Detect and analyze language errors in the user's message.
    
    Args:
        message (str): The user's message text
        target_language (str): The language the user is learning
        proficiency_level (str): The user's proficiency level
        
    Returns:
        list: A list of dictionaries containing error details:
             [{"error_text": "...", "correction": "...", "error_type": "..."}]
    """
    api_key = current_app.config.get('OPENROUTER_API_KEY')
    
    if not api_key:
        logger.error("OpenRouter API key is not set")
        return []
    
    # If the message is too short, it's hard to find meaningful errors
    if len(message.split()) < 2:
        return []
    
    # System prompt for error detection
    system_prompt = f"""You are a language tutor analyzing text in {target_language} from a {proficiency_level.lower()} level student.
Your task is to identify grammar, vocabulary, and syntax errors in their message.
For each error:
1. Identify the specific error text
2. Provide the correct form
3. Classify the error type (grammar, vocabulary, syntax)

FORMAT YOUR RESPONSE AS JSON:
{{
  "errors": [
    {{
      "error_text": "[text with error]",
      "correction": "[corrected text]",
      "error_type": "[grammar|vocabulary|syntax]"
    }}
  ]
}}

If there are no errors, return an empty array for "errors".
ONLY RETURN VALID JSON. Do not include any explanations or text before or after the JSON.
"""
    
    # Prepare request to OpenRouter API
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": current_app.config.get('OPENROUTER_MODEL', 'google/gemini-pro-1.5-experimental'),
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message}
        ],
        "response_format": {"type": "json_object"}
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
            return []
        
        response_data = response.json()
        content = response_data['choices'][0]['message']['content'].strip()
        
        # Parse the JSON response
        try:
            error_data = json.loads(content)
            return error_data.get('errors', [])
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON from API: {str(e)} - Content: {content}")
            return []
        
    except Exception as e:
        logger.error(f"Error detecting language errors: {str(e)}")
        return []
