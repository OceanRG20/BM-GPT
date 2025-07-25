import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
BASE_PROMPT = os.getenv("BASE_PROMPT")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o")
TESSERACT_CMD = os.getenv("TESSERACT_CMD")

if not OPENAI_API_KEY:
    raise ValueError("❌ OPENAI_API_KEY is missing from .env")
