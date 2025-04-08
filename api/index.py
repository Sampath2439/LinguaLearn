"""
Vercel serverless entry point for the LinguaBot application.
"""

import os
import sys

# Add the parent directory to the path so we can import from the root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app as application

# This is the handler that Vercel serverless functions use
def handler(event, context):
    """Handle incoming HTTP requests in the Vercel serverless environment."""
    return application(event, context)

# For local development
if __name__ == "__main__":
    application.run(host="0.0.0.0", port=5000, debug=True)