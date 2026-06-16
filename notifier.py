import queue
import threading
import time

import requests
from config import DISCORD_WEBHOOK, get_keyword_webhooks

_discord_queue = queue.Queue()
_worker_started = False
_worker_lock = threading.Lock()


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


def _discord_worker():
    while True:
        webhooks, message = _discord_queue.get()

        try:
            for webhook in webhooks:
                response = requests.post(webhook, json=message, timeout=10)

                if response.status_code == 429:
                    retry_after = response.json().get("retry_after", 1)
                    time.sleep(float(retry_after))
                    response = requests.post(webhook, json=message, timeout=10)

                if response.status_code >= 400:
                    print(
                        "discord webhook failed:",
                        response.status_code,
                        response.text[:200],
                    )

                time.sleep(0.4)

        except Exception as e:
            print("discord webhook failed:", e)

        finally:
            _discord_queue.task_done()
            time.sleep(0.2)


def _ensure_worker():
    global _worker_started

    with _worker_lock:
        if not _worker_started:
            threading.Thread(target=_discord_worker, daemon=True).start()
            _worker_started = True


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

    _ensure_worker()
    _discord_queue.put((webhooks, message))
