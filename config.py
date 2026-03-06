import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
REQUIRED_CHANNEL = os.getenv("REQUIRED_CHANNEL")
REQUIRED_CHANNEL_URL = os.getenv("REQUIRED_CHANNEL_URL")

DEFAULT_COINS = 20

SUPPORTED_LANGUAGES = ["ar", "en", "de", "tr"]

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is missing.")

if not REQUIRED_CHANNEL:
    raise ValueError("REQUIRED_CHANNEL is missing.")

if not REQUIRED_CHANNEL_URL:
    raise ValueError("REQUIRED_CHANNEL_URL is missing.")