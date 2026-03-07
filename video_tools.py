import time
import requests
from config import OPENAI_API_KEY, OPENAI_VIDEO_MODEL


BASE_URL = "https://api.openai.com/v1/videos"


def _headers():
    return {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }


def create_video_job(prompt: str, seconds: int, aspect_ratio: str):
    payload = {
        "model": OPENAI_VIDEO_MODEL,
        "prompt": prompt,
        "seconds": seconds,
        "aspect_ratio": aspect_ratio,
    }

    response = requests.post(BASE_URL, headers=_headers(), json=payload, timeout=120)
    response.raise_for_status()
    return response.json()


def get_video(video_id: str):
    response = requests.get(f"{BASE_URL}/{video_id}", headers=_headers(), timeout=120)
    response.raise_for_status()
    return response.json()


def download_video_bytes(video_id: str) -> bytes:
    response = requests.get(f"{BASE_URL}/{video_id}/content", headers=_headers(), timeout=300)
    response.raise_for_status()
    return response.content


def wait_for_video(video_id: str, max_wait_seconds: int = 900, poll_every: int = 10):
    start = time.time()

    while time.time() - start < max_wait_seconds:
        data = get_video(video_id)
        status = data.get("status", "").lower()

        if status in {"completed", "succeeded", "ready"}:
            return data

        if status in {"failed", "error", "cancelled"}:
            raise RuntimeError(f"Video generation failed: {data}")

        time.sleep(poll_every)

    raise TimeoutError("Video generation timed out")