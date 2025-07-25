import openai
import base64
import os
from dotenv import load_dotenv
from markdown import markdown  # for Markdown to HTML rendering

# Load environment variables
load_dotenv()

# Environment config
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o")

if not OPENAI_API_KEY:
    raise ValueError("\u274c OPENAI_API_KEY is missing from .env")

openai.api_key = OPENAI_API_KEY

# GPT-4o-style refined and structured prompt
GPT4O_SYSTEM_PROMPT = {
    "role": "system",
    "content": (
        "You are GPT-4o, a brilliant and articulate AI assistant created by OpenAI.\n"
        "Always provide answers that are:\n"
        "- Complete and well-reasoned\n"
        "- Structured with clear headers, bullet points, or numbered lists\n"
        "- Formatted professionally using Markdown (e.g., **bold**, _italic_, code blocks)\n"
        "- Adaptable to different question styles (casual, technical, formal)\n"
        "- Aware of multiple meanings and able to distinguish between them\n"
        "- Can include appropriate emoji or symbol or inline image URL markdown if useful (e.g., `![chart](url)` or `📈`)\n\n"
        "Avoid vague explanations or cluttered formatting. Always present polished, clear, and beautifully formatted output as if answering in a professional interface like ChatGPT."
    )
}

class ChatGPTClient:
    def ask_manual(self, message):
        try:
            response = openai.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    GPT4O_SYSTEM_PROMPT,
                    {"role": "user", "content": message}
                ],
                temperature=0.65,
                max_tokens=1200,
                response_format={"type": "text"}  # explicitly define correct format as object
            )
            return self.markdown_to_html(response.choices[0].message.content.strip())
        except Exception as e:
            return f"\u26a0\ufe0f GPT Error: {e}"

    def ask_auto_image(self, image_path):
        try:
            with open(image_path, "rb") as f:
                b64_image = base64.b64encode(f.read()).decode()

            response = openai.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    GPT4O_SYSTEM_PROMPT,
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/png;base64,{b64_image}"}
                            },
                            {
                                "type": "text",
                                "text": (
                                    "Please analyze the image as a trading expert. Explain:\n"
                                    "- Market sentiment (bullish/bearish)\n"
                                    "- Notable liquidity zones and order flow\n"
                                    "- Any spoofing, absorption, or breakout signals\n\n"
                                    "Present the results with professional formatting like headers, bullet points, and use emojis or markdown visuals if helpful."
                                )
                            }
                        ]
                    }
                ],
                temperature=0.6,
                max_tokens=1000,
                response_format={"type": "text"}  # explicitly define correct format as object
            )
            return self.markdown_to_html(response.choices[0].message.content.strip())
        except Exception as e:
            return f"\u26a0\ufe0f GPT Error: {e}"

    def markdown_to_html(self, md_text):
        # Ensure image and layout consistency for both manual and auto mode
        html = markdown(md_text, extensions=["fenced_code", "tables", "nl2br"])
        return html.replace('<img', '<img style="max-width:100%; height:auto;"')