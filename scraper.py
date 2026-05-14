import asyncio

import mercapi
from mercapi.requests import SearchRequestData

from database import (
    get_keywords,
    is_keyword_baselined,
    item_exists,
    mark_item_seen,
    save_item,
    set_keyword_baselined,
)

from notifier import send_discord_notification


def _item_payload(item, keyword):
    return {
        "id": str(item.id_),
        "keyword": keyword,
        "title": item.name,
        "price": item.real_price if item.real_price is not None else item.price,
        "url": f"https://jp.mercari.com/item/{item.id_}",
        "image": item.thumbnails[0] if item.thumbnails else "",
    }


async def search_keyword(keyword):
    client = mercapi.Mercapi()
    baselined = is_keyword_baselined(keyword)

    print(f"Searching: {keyword}")

    try:
        results = await client.search(
            keyword,
            sort_by=SearchRequestData.SortBy.SORT_CREATED_TIME,
            sort_order=SearchRequestData.SortOrder.ORDER_DESC,
        )

        if not baselined:
            for item in results.items:
                mark_item_seen(str(item.id_), keyword)

            set_keyword_baselined(keyword)
            print(f"Baselined {len(results.items)} existing listings for: {keyword}")
            return

        for item in results.items:
            item_id = str(item.id_)

            if item_exists(item_id):
                continue

            parsed_item = _item_payload(item, keyword)

            save_item(parsed_item)
            send_discord_notification(parsed_item)

            print(f"NEW ITEM: {item.name}")

    except Exception as e:
        print(f"Error searching {keyword}:", e)


async def run_scraper():
    keywords = get_keywords()

    if not keywords:
        print("No keywords added.")
        return

    tasks = [search_keyword(keyword) for keyword in keywords]

    await asyncio.gather(*tasks)
