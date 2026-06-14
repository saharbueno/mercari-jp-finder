import requests
from config import DISCORD_WEBHOOK, KEYWORD_WEBHOOKS


def _webhook_for_keyword(keyword):
    return KEYWORD_WEBHOOKS.get(keyword) or DISCORD_WEBHOOK


def send_discord_notification(item):
    webhook = _webhook_for_keyword(item["keyword"])

    if not webhook:
        return

    message = {
        "content": (
            "₊˚⊹ **♡ new mercari listing ♡** ⊹˚₊\n"
            "　　｡ ₊°༺❤︎༻°₊ ｡\n"
            "╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌\n"
            f"♡ **keyword** ❤︎₊ ⊹ `{item['keyword']}`\n"
            f"♡ **price** ݁˖❤︎ྀ ¥{item['price']:,}\n"
            f"♡ **title** ˚₊‧꒰ა❤︎໒꒱ ‧₊\n"
            f"　　{item['title']}\n"
            "╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌\n"
            f"⊹₊˚ **link** ♡ {item['url']}\n"
            "₊˚⊹ (๑˃ᴗ˂)ﻭ ♡ ⊹˚₊"
        )
    }

    try:
        requests.post(webhook, json=message)

    except Exception as e:
        print("discord webhook failed:", e)