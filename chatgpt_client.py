import openai
from config import OPENAI_API_KEY, MODEL_NAME, BASE_PROMPT

openai.api_key = OPENAI_API_KEY

class ChatGPTClient:
    def ask(self, message):
        try:
            messages = [
                {"role": "system", "content": BASE_PROMPT},
                {"role": "user", "content": message}
            ]
            response = openai.chat.completions.create(
                model=MODEL_NAME,
                messages=messages,
                temperature=0.4,
                max_tokens=300
            )
            return response.choices[0].message.content.strip()
        except openai.AuthenticationError as e:
            return f"❌ Authentication Error: {e}"
        except openai.RateLimitError as e:
            return f"🚫 Rate Limit Error: {e}"
        except Exception as e:
            return f"⚠️ GPT Error: {e}"
