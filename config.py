import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
BASE_PROMPT = os.getenv("BASE_PROMPT", "You are a professional trading assistant. Given market data, generate trading commentary.")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o")

if not OPENAI_API_KEY:
    raise ValueError("❌ OPENAI_API_KEY is missing from .env")
