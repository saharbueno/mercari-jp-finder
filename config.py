import json
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def _load_keyword_webhooks():
    webhooks = {}

    env_webhooks = os.getenv("KEYWORD_WEBHOOKS")
    if env_webhooks:
        webhooks.update(json.loads(env_webhooks))

    webhooks_file = Path("keyword_webhooks.json")
    if webhooks_file.exists():
        webhooks.update(json.loads(webhooks_file.read_text(encoding="utf-8")))

    return webhooks


DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")
KEYWORD_WEBHOOKS = _load_keyword_webhooks()
POLL_INTERVAL_SECONDS = int(os.getenv("POLL_INTERVAL_SECONDS", 60))
PORT = int(os.getenv("PORT", 5001))