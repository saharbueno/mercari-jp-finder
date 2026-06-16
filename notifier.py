import queue
import threading
import time

import requests
from config import CUSHION_KEYWORD, DISCORD_WEBHOOK, get_cushion_webhook

_discord_queue = queue.Queue()
_worker_started = False
_worker_lock = threading.Lock()


def _build_message(item):
    return {
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


def _post_message(webhook, message):
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
        return False

    return True


def _discord_worker():
    while True:
        channel, webhook, message = _discord_queue.get()

        try:
            if _post_message(webhook, message):
                print(f"sent alert to {channel}: {message['content'].split(chr(10))[5][:50]}")

        except Exception as e:
            print(f"discord webhook failed ({channel}):", e)

        finally:
            _discord_queue.task_done()
            time.sleep(0.3)


def _ensure_worker():
    global _worker_started

    with _worker_lock:
        if not _worker_started:
            threading.Thread(target=_discord_worker, daemon=True).start()
            _worker_started = True


def _queue_alert(channel, webhook, message):
    if not webhook:
        return

    _ensure_worker()
    _discord_queue.put((channel, webhook, message))


def send_discord_notification(item):
    keyword = item["keyword"].strip()
    message = _build_message(item)

    _queue_alert("general", DISCORD_WEBHOOK, message)

    if keyword == CUSHION_KEYWORD:
        cushion_webhook = get_cushion_webhook()
        _queue_alert("cushion", cushion_webhook, message)

        if not cushion_webhook:
            print(f"cushion listing found but no cushion webhook configured: {item['title']}")
