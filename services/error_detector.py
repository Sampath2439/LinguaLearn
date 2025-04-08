import json
import logging
from flask import current_app
from openai import OpenAI

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
    
    # Initialize OpenAI client with OpenRouter endpoint
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key
    )
    
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
    
    try:
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
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ],
            response_format={"type": "json_object"}
        )
        
        content = completion.choices[0].message.content.strip()
        
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
