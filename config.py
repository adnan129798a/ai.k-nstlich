import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
REQUIRED_CHANNEL = os.getenv("REQUIRED_CHANNEL")
REQUIRED_CHANNEL_URL = os.getenv("REQUIRED_CHANNEL_URL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

OPENAI_TEXT_MODEL = os.getenv("OPENAI_TEXT_MODEL", "gpt-4.1-mini")
OPENAI_IMAGE_MODEL = os.getenv("OPENAI_IMAGE_MODEL", "gpt-image-1")
OPENAI_VIDEO_MODEL = os.getenv("OPENAI_VIDEO_MODEL", "sora-2")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is missing.")

if not REQUIRED_CHANNEL:
    raise ValueError("REQUIRED_CHANNEL is missing.")

if not REQUIRED_CHANNEL_URL:
    raise ValueError("REQUIRED_CHANNEL_URL is missing.")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is missing.")