import requests
from config import DISCORD_WEBHOOK, get_keyword_webhooks


def _webhooks_for_keyword(keyword):
    keyword = keyword.strip()
    webhooks = []
    keyword_webhooks = get_keyword_webhooks()

    specific = keyword_webhooks.get(keyword)
    if specific:
        webhooks.append(specific)

    if DISCORD_WEBHOOK and DISCORD_WEBHOOK not in webhooks:
        webhooks.append(DISCORD_WEBHOOK)

    return webhooks


def send_discord_notification(item):
    webhooks = _webhooks_for_keyword(item["keyword"])

    if not webhooks:
        print(f"no discord webhooks configured for keyword: {item['keyword']}")
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

    for webhook in webhooks:
        try:
            response = requests.post(webhook, json=message, timeout=10)

            if response.status_code >= 400:
                print(
                    "discord webhook failed:",
                    response.status_code,
                    response.text[:200],
                )

        except Exception as e:
            print("discord webhook failed:", e)