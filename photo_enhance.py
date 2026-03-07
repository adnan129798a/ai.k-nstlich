from io import BytesIO
from PIL import Image, ImageEnhance, ImageFilter


def _open_image(image_bytes: bytes) -> Image.Image:
    img = Image.open(BytesIO(image_bytes)).convert("RGB")
    return img


def _save_image(img: Image.Image) -> bytes:
    out = BytesIO()
    img.save(out, format="JPEG", quality=95)
    return out.getvalue()


def auto_enhance(image_bytes: bytes) -> bytes:
    img = _open_image(image_bytes)

    img = ImageEnhance.Brightness(img).enhance(1.06)
    img = ImageEnhance.Contrast(img).enhance(1.08)
    img = ImageEnhance.Color(img).enhance(1.05)
    img = img.filter(ImageFilter.SHARPEN)

    return _save_image(img)


def brighten(image_bytes: bytes) -> bytes:
    img = _open_image(image_bytes)
    img = ImageEnhance.Brightness(img).enhance(1.12)
    return _save_image(img)


def contrast(image_bytes: bytes) -> bytes:
    img = _open_image(image_bytes)
    img = ImageEnhance.Contrast(img).enhance(1.15)
    return _save_image(img)


def smooth(image_bytes: bytes) -> bytes:
    img = _open_image(image_bytes)
    img = img.filter(ImageFilter.SMOOTH_MORE)
    return _save_image(img)


def sharpen(image_bytes: bytes) -> bytes:
    img = _open_image(image_bytes)
    img = ImageEnhance.Sharpness(img).enhance(1.35)
    return _save_image(img)


def color_boost(image_bytes: bytes) -> bytes:
    img = _open_image(image_bytes)
    img = ImageEnhance.Color(img).enhance(1.12)
    return _save_image(img)


def custom_edit(image_bytes: bytes, text: str) -> bytes:
    t = text.lower()
    img = _open_image(image_bytes)

    brightness = 1.0
    contrast_v = 1.0
    sharpness = 1.0
    color_v = 1.0
    smooth_flag = False

    if "تفتيح" in text or "bright" in t:
        brightness = 1.10
    if "تباين" in text or "contrast" in t:
        contrast_v = 1.12
    if "وضوح" in text or "حدة" in text or "sharp" in t:
        sharpness = 1.20
    if "ألوان" in text or "الوان" in text or "color" in t:
        color_v = 1.10
    if "تنعيم" in text or "smooth" in t:
        smooth_flag = True

    img = ImageEnhance.Brightness(img).enhance(brightness)
    img = ImageEnhance.Contrast(img).enhance(contrast_v)
    img = ImageEnhance.Color(img).enhance(color_v)
    img = ImageEnhance.Sharpness(img).enhance(sharpness)

    if smooth_flag:
        img = img.filter(ImageFilter.SMOOTH_MORE)

    return _save_image(img)