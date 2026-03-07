import requests
import time
from config import OPENAI_API_KEY, OPENAI_VIDEO_MODEL


headers = {
    "Authorization": f"Bearer {OPENAI_API_KEY}",
    "Content-Type": "application/json"
}


def create_video_job(prompt, seconds=15, aspect_ratio="9:16"):

    url = "https://api.openai.com/v1/videos"

    data = {
        "model": OPENAI_VIDEO_MODEL,
        "prompt": prompt,
        "seconds": seconds,
        "aspect_ratio": aspect_ratio
    }

    r = requests.post(url, headers=headers, json=data)

    if r.status_code != 200:
        raise Exception(r.text)

    return r.json()


def wait_for_video(video_id):

    url = f"https://api.openai.com/v1/videos/{video_id}"

    while True:

        r = requests.get(url, headers=headers)
        data = r.json()

        status = data.get("status")

        if status == "completed":
            return data

        if status == "failed":
            raise Exception("Video generation failed")

        time.sleep(5)


def download_video_bytes(video_id):

    url = f"https://api.openai.com/v1/videos/{video_id}/content"

    r = requests.get(url, headers=headers)

    if r.status_code != 200:
        raise Exception(r.text)

    return r.content