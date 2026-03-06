from openai import OpenAI

from config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)


def ask_ai(prompt: str) -> str:
    response = client.responses.create(
        model="gpt-5.4",
        input=prompt
    )
    return response.output_text.strip()