from openai import OpenAI
from config import OPENAI_API_KEY, OPENAI_VIDEO_MODEL

client = OpenAI(api_key=OPENAI_API_KEY)


def ratio_to_size(ratio: str) -> str:
    mapping = {
        "9:16": "720x1280",
        "16:9": "1280x720",
        "1:1": "1024x1792",  # أقرب خيار مدعوم حاليًا، لأن 1:1 غير ظاهر في القيم الرسمية
    }
    return mapping.get(ratio, "720x1280")


def seconds_to_allowed(seconds: int) -> int:
    # API الحالية تدعم فقط 4 / 8 / 12
    if seconds <= 4:
        return 4
    if seconds <= 8:
        return 8
    return 12


def create_video_job(prompt: str, seconds: int = 12, aspect_ratio: str = "9:16"):
    allowed_seconds = seconds_to_allowed(seconds)
    size = ratio_to_size(aspect_ratio)

    video = client.videos.create(
        model=OPENAI_VIDEO_MODEL,
        prompt=prompt,
        seconds=str(allowed_seconds),
        size=size,
    )
    return video


def wait_for_video(video_id: str, max_checks: int = 180):
    for _ in range(max_checks):
        video = client.videos.retrieve(video_id)

        status = getattr(video, "status", "")
        if status == "completed":
            return video

        if status == "failed":
            error = getattr(video, "error", None)
            message = getattr(error, "message", "Video generation failed")
            raise Exception(message)

        import time
        time.sleep(5)

    raise Exception("Video generation timed out")


def download_video_bytes(video_id: str) -> bytes:
    content = client.videos.download_content(video_id, variant="video")
    return content.read()