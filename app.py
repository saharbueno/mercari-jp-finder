import os
import threading
from datetime import datetime

from flask import Flask, render_template, request, redirect

from apscheduler.schedulers.background import BackgroundScheduler

import asyncio

from scraper import run_scraper

from database import (
    get_keywords,
    add_keyword,
    delete_keyword,
    get_recent_items
)

from config import POLL_INTERVAL_SECONDS, PORT

app = Flask(__name__)

_scrape_lock = threading.Lock()


@app.route("/")
def index():
    keywords = get_keywords()
    items = get_recent_items()

    return render_template(
        "index.html",
        keywords=keywords,
        items=items
    )


@app.route("/add", methods=["POST"])
def add():
    keyword = request.form.get("keyword", "").strip()

    if keyword:
        add_keyword(keyword)

    return redirect("/")


@app.route("/delete/<path:keyword>")
def delete(keyword):
    delete_keyword(keyword)

    return redirect("/")


# BACKGROUND SCRAPER

def scheduled_scrape():
    if not _scrape_lock.acquire(blocking=False):
        print("Scrape already running, skipping...")
        return

    print("Running scheduled scrape...")

    try:
        asyncio.run(run_scraper())

    except Exception as e:
        print("Scraper error:", e)

    finally:
        _scrape_lock.release()


scheduler = BackgroundScheduler()

if os.environ.get("WERKZEUG_RUN_MAIN") == "true" or not app.debug:
    scheduler.add_job(
        func=scheduled_scrape,
        trigger="interval",
        seconds=POLL_INTERVAL_SECONDS,
        next_run_time=datetime.now(),
        max_instances=1,
        coalesce=True,
        misfire_grace_time=120,
    )

    scheduler.start()


if __name__ == "__main__":
    print("Mercari JP Finder started.")

    app.run(
        debug=True,
        use_reloader=False,
        host="0.0.0.0",
        port=PORT
    )