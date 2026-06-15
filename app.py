import os

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
    print("Running scheduled scrape...")

    try:
        asyncio.run(run_scraper())

    except Exception as e:
        print("Scraper error:", e)


scheduler = BackgroundScheduler()

if os.environ.get("WERKZEUG_RUN_MAIN") == "true" or not app.debug:
    scheduler.add_job(
        func=scheduled_scrape,
        trigger="interval",
        seconds=POLL_INTERVAL_SECONDS
    )

    scheduler.start()


if __name__ == "__main__":
    print("Mercari JP Finder started.")

    # Run one scrape immediately on startup (skip parent reloader process)
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true" or not app.debug:
        scheduled_scrape()

    app.run(
        debug=True,
        host="0.0.0.0",
        port=PORT
    )