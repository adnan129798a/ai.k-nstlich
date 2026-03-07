import base64
import tempfile
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
        return (
            f"{user_prompt}, anime style, preserve same identity as much as possible, "
            f"similar facial structure, similar hairstyle, detailed anime, clean line art"
        )
    if style == "cinematic":
        return f"{user_prompt}, cinematic scene, dramatic lighting, movie still, high detail"
    if style == "hyper_real":
        return (
            f"{user_prompt}, ultra realistic, photorealistic, realistic face, realistic skin texture, "
            f"realistic eyes, realistic hands, cinematic lighting, professional photography, sharp focus"
        )
    return build_realistic_prompt(user_prompt)


def generate_image_bytes(user_prompt: str, style: str = "realistic") -> bytes:
    prompt = build_realistic_prompt(user_prompt) if style == "realistic" else build_stylized_prompt(user_prompt, style)

    result = client.images.generate(
        model=OPENAI_IMAGE_MODEL,
        prompt=prompt,
        size="1024x1024",
        quality="medium"
    )

    image_b64 = result.data[0].b64_json
    return base64.b64decode(image_b64)


def edit_image_bytes(image_bytes: bytes, instruction: str) -> bytes:
    with tempfile.NamedTemporaryFile(suffix=".jpg") as temp_img:
        temp_img.write(image_bytes)
        temp_img.flush()

        with open(temp_img.name, "rb") as img_file:
            result = client.images.edit(
                model=OPENAI_IMAGE_MODEL,
                image=img_file,
                prompt=instruction,
                size="1024x1024"
            )

    image_b64 = result.data[0].b64_json
    return base64.b64decode(image_b64)