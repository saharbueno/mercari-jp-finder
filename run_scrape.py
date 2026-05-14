import asyncio

from scraper import run_scraper
from sync_keywords import sync_keywords_from_file


def main():
    added, removed = sync_keywords_from_file()

    if added:
        print("Added keywords:", ", ".join(added))

    if removed:
        print("Removed keywords:", ", ".join(removed))

    asyncio.run(run_scraper())


if __name__ == "__main__":
    main()
