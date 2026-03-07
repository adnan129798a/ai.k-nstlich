from io import BytesIO
from PIL import Image, ImageEnhance, ImageFilter


def _open_image(image_bytes: bytes) -> Image.Image:
    return Image.open(BytesIO(image_bytes)).convert("RGB")


def _save_image(img: Image.Image) -> bytes:
    out = BytesIO()
    img.save(out, format="JPEG", quality=95)
    return out.getvalue()


def auto_enhance(image_bytes: bytes) -> bytes:
    img = _open_image(image_bytes)
    img = ImageEnhance.Brightness(img).enhance(1.12)
    img = ImageEnhance.Contrast(img).enhance(1.16)
    img = ImageEnhance.Color(img).enhance(1.10)
    img = ImageEnhance.Sharpness(img).enhance(1.18)
    return _save_image(img)


def brighten(image_bytes: bytes) -> bytes:
    img = _open_image(image_bytes)
    img = ImageEnhance.Brightness(img).enhance(1.18)
    return _save_image(img)


def contrast(image_bytes: bytes) -> bytes:
    img = _open_image(image_bytes)
    img = ImageEnhance.Contrast(img).enhance(1.22)
    return _save_image(img)


def smooth(image_bytes: bytes) -> bytes:
    img = _open_image(image_bytes)
    img = img.filter(ImageFilter.SMOOTH_MORE)
    img = img.filter(ImageFilter.SMOOTH_MORE)
    return _save_image(img)


def sharpen(image_bytes: bytes) -> bytes:
    img = _open_image(image_bytes)
    img = ImageEnhance.Sharpness(img).enhance(1.45)
    return _save_image(img)


def color_boost(image_bytes: bytes) -> bytes:
    img = _open_image(image_bytes)
    img = ImageEnhance.Color(img).enhance(1.18)
    return _save_image(img)


def custom_edit(image_bytes: bytes, text: str) -> bytes:
    t = text.lower()
    img = _open_image(image_bytes)

    brightness = 1.0
    contrast_v = 1.0
    sharpness = 1.0
    color_v = 1.0
    smooth_times = 0

    if "تفتيح" in text or "bright" in t:
        brightness = 1.16
    if "تباين" in text or "contrast" in t:
        contrast_v = 1.18
    if "وضوح" in text or "حدة" in text or "sharp" in t:
        sharpness = 1.30
    if "ألوان" in text or "الوان" in text or "color" in t:
        color_v = 1.15
    if "تنعيم" in text or "smooth" in t:
        smooth_times = 2

    img = ImageEnhance.Brightness(img).enhance(brightness)
    img = ImageEnhance.Contrast(img).enhance(contrast_v)
    img = ImageEnhance.Color(img).enhance(color_v)
    img = ImageEnhance.Sharpness(img).enhance(sharpness)

    for _ in range(smooth_times):
        img = img.filter(ImageFilter.SMOOTH_MORE)

    return _save_image(img)