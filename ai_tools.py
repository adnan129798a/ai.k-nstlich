from openai import OpenAI
from config import OPENAI_API_KEY, OPENAI_TEXT_MODEL

client = OpenAI(api_key=OPENAI_API_KEY)


def ask_ai(prompt: str) -> str:
    response = client.responses.create(
        model=OPENAI_TEXT_MODEL,
        input=prompt
    )
    return (response.output_text or "").strip()