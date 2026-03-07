import base64
from openai import OpenAI
from config import OPENAI_API_KEY, OPENAI_IMAGE_MODEL

client = OpenAI(api_key=OPENAI_API_KEY)


def build_realistic_prompt(user_prompt: str) -> str:
    return (
        f"{user_prompt}, ultra realistic, photorealistic, realistic human proportions, "
        f"realistic face, realistic skin texture, realistic eyes, realistic hands, "
        f"professional photography, cinematic lighting, high detail, sharp focus"
    )


def build_stylized_prompt(user_prompt: str, style: str) -> str:
    if style == "anime":
        return f"{user_prompt}, anime style, highly detailed, vibrant colors, clean line art"
    if style == "cinematic":
        return f"{user_prompt}, cinematic scene, dramatic lighting, movie still, high detail"
    if style == "hyper_real":
        return (
            f"{user_prompt}, ultra realistic, photorealistic, realistic face, realistic skin texture, "
            f"realistic eyes, realistic hands, cinematic lighting, professional photography, sharp focus"
        )
    return build_realistic_prompt(user_prompt)


def generate_image_bytes(user_prompt: str, style: str = "realistic") -> bytes:
    if style == "realistic":
        prompt = build_realistic_prompt(user_prompt)
    else:
        prompt = build_stylized_prompt(user_prompt, style)

    result = client.images.generate(
        model=OPENAI_IMAGE_MODEL,
        prompt=prompt,
        size="1024x1024",
        quality="medium"
    )

    image_b64 = result.data[0].b64_json
    return base64.b64decode(image_b64)