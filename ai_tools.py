from openai import OpenAI
from config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

def ask_ai(prompt: str) -> str:
    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=prompt
        )
        return response.output_text.strip() if response.output_text else "لم يصل رد من الذكاء الاصطناعي."
    except Exception as e:
        return f"AI ERROR: {str(e)}"