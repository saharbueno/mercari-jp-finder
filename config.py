import json
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

CUSHION_KEYWORDS = {
    "マイメロディクッション",
    "マイメロクッション",
}


def is_cushion_keyword(keyword):
    return keyword.strip() in CUSHION_KEYWORDS


def get_cushion_webhook():
    cushion_webhook = os.getenv("DISCORD_WEBHOOK_CUSHION")

    if cushion_webhook:
        return cushion_webhook

    webhooks_file = Path("keyword_webhooks.json")
    if webhooks_file.exists():
        file_webhooks = json.loads(webhooks_file.read_text(encoding="utf-8"))
        return file_webhooks.get("マイメロディクッション")

    env_webhooks = os.getenv("KEYWORD_WEBHOOKS")
    if env_webhooks:
        return json.loads(env_webhooks).get("マイメロディクッション")

    return None


DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")
POLL_INTERVAL_SECONDS = int(os.getenv("POLL_INTERVAL_SECONDS", 60))
PORT = int(os.getenv("PORT", 5001))
