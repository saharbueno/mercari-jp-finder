import requests
from config import DISCORD_WEBHOOK, KEYWORD_WEBHOOKS


def _webhooks_for_keyword(keyword):
    keyword = keyword.strip()
    webhooks = []

    specific = KEYWORD_WEBHOOKS.get(keyword)
    if specific:
        webhooks.append(specific)

    if DISCORD_WEBHOOK and DISCORD_WEBHOOK not in webhooks:
        webhooks.append(DISCORD_WEBHOOK)

    return webhooks


def send_discord_notification(item):
    webhooks = _webhooks_for_keyword(item["keyword"])

    if not webhooks:
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
        for webhook in webhooks:
            requests.post(webhook, json=message)

    except Exception as e:
        print("discord webhook failed:", e)