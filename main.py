import logging
from app import app

# Configure logging to see detailed logs
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
