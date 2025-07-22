import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Fetch variables from .env
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
BASE_PROMPT = os.getenv("BASE_PROMPT", "You are a professional trading assistant. Given the current order book and market data, provide a concise trading insight.")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o")  # Default to gpt-4o if not defined

# Debug (Optional: remove in production)
if not OPENAI_API_KEY:
    raise ValueError("❌ OPENAI_API_KEY is not set in the .env file!")