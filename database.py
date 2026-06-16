import sqlite3
import os
from datetime import datetime, timezone

DB_PATH = "data/listings.db"


def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS keywords (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            keyword TEXT UNIQUE,
            tracked_since TEXT,
            baselined INTEGER NOT NULL DEFAULT 0
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS seen_items (
            item_id TEXT PRIMARY KEY,
            keyword TEXT,
            title TEXT,
            price INTEGER,
            url TEXT,
            image TEXT,
            is_alert INTEGER NOT NULL DEFAULT 0
        )
        """
    )

    _migrate_schema(cursor)

    conn.commit()
    conn.close()


def _migrate_schema(cursor):
    keyword_columns = {
        row[1] for row in cursor.execute("PRAGMA table_info(keywords)")
    }
    if "tracked_since" not in keyword_columns:
        cursor.execute("ALTER TABLE keywords ADD COLUMN tracked_since TEXT")
        cursor.execute(
            "UPDATE keywords SET tracked_since = ? WHERE tracked_since IS NULL",
            (datetime.now(timezone.utc).isoformat(),),
        )

    if "baselined" not in keyword_columns:
        cursor.execute(
            "ALTER TABLE keywords ADD COLUMN baselined INTEGER NOT NULL DEFAULT 0"
        )
        cursor.execute("UPDATE keywords SET baselined = 1 WHERE baselined = 0")

    item_columns = {
        row[1] for row in cursor.execute("PRAGMA table_info(seen_items)")
    }
    if "is_alert" not in item_columns:
        cursor.execute(
            "ALTER TABLE seen_items ADD COLUMN is_alert INTEGER NOT NULL DEFAULT 0"
        )

    if "cushion_alerted" not in item_columns:
        cursor.execute(
            "ALTER TABLE seen_items ADD COLUMN cushion_alerted INTEGER NOT NULL DEFAULT 0"
        )

    cursor.execute(
        "SELECT 1 FROM app_meta WHERE key='cushion_alerted_v1'"
    )
    if cursor.fetchone() is None:
        cursor.execute("UPDATE seen_items SET cushion_alerted = 1")
        cursor.execute(
            "INSERT INTO app_meta(key, value) VALUES ('cushion_alerted_v1', '1')"
        )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS app_meta (
            key TEXT PRIMARY KEY,
            value TEXT
        )
        """
    )
    cursor.execute(
        "SELECT 1 FROM app_meta WHERE key='rebaseline_sort_v1'"
    )
    if cursor.fetchone() is None:
        cursor.execute("UPDATE keywords SET baselined = 0")
        cursor.execute("UPDATE seen_items SET is_alert = 0")
        cursor.execute(
            "INSERT INTO app_meta(key, value) VALUES ('rebaseline_sort_v1', '1')"
        )

    cursor.execute(
        "SELECT 1 FROM app_meta WHERE key='trim_keywords_v1'"
    )
    if cursor.fetchone() is None:
        cursor.execute("UPDATE keywords SET keyword = TRIM(keyword)")
        cursor.execute(
            "UPDATE seen_items SET keyword = TRIM(keyword) WHERE keyword IS NOT NULL"
        )
        cursor.execute(
            "INSERT INTO app_meta(key, value) VALUES ('trim_keywords_v1', '1')"
        )


init_db()


# KEYWORDS

def get_keywords():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT keyword FROM keywords")

    keywords = [row[0] for row in cursor.fetchall()]

    conn.close()

    return keywords


def add_keyword(keyword):
    keyword = keyword.strip()

    if not keyword:
        return

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO keywords(keyword, tracked_since, baselined)
            VALUES (?, ?, 0)
            """,
            (keyword, datetime.now(timezone.utc).isoformat()),
        )

        conn.commit()

    except Exception:
        pass

    conn.close()


def get_keyword_tracked_since(keyword):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT tracked_since FROM keywords WHERE keyword=?",
        (keyword,),
    )

    row = cursor.fetchone()
    conn.close()

    if not row or not row[0]:
        return datetime.now(timezone.utc)

    return datetime.fromisoformat(row[0])


def is_keyword_baselined(keyword):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT baselined FROM keywords WHERE keyword=?",
        (keyword,),
    )

    row = cursor.fetchone()
    conn.close()

    return bool(row and row[0])


def set_keyword_baselined(keyword):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE keywords SET baselined = 1 WHERE keyword=?",
        (keyword,),
    )

    conn.commit()
    conn.close()


def delete_keyword(keyword):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM keywords WHERE keyword=?",
        (keyword,)
    )

    conn.commit()
    conn.close()


# ITEMS

def item_exists(item_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT 1 FROM seen_items WHERE item_id=?",
        (item_id,)
    )

    exists = cursor.fetchone() is not None

    conn.close()

    return exists


def item_cushion_alerted(item_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT cushion_alerted FROM seen_items WHERE item_id=?",
        (item_id,),
    )

    row = cursor.fetchone()
    conn.close()

    return bool(row and row[0])


def mark_cushion_alerted(item_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE seen_items SET cushion_alerted = 1 WHERE item_id=?",
        (item_id,),
    )

    conn.commit()
    conn.close()


def mark_item_seen(item_id, keyword, cushion_alerted=False):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT OR IGNORE INTO seen_items(item_id, keyword, is_alert, cushion_alerted)
        VALUES (?, ?, 0, ?)
        """,
        (item_id, keyword, 1 if cushion_alerted else 0),
    )

    conn.commit()
    conn.close()


def save_item(item):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO seen_items(
            item_id, keyword, title, price, url, image, is_alert, cushion_alerted
        )
        VALUES (?, ?, ?, ?, ?, ?, 1, 0)
        """,
        (
            item["id"],
            item["keyword"],
            item["title"],
            item["price"],
            item["url"],
            item["image"],
        ),
    )

    conn.commit()
    conn.close()


def get_recent_items(limit=50):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT keyword, title, price, url, image
        FROM seen_items
        WHERE is_alert = 1
        ORDER BY rowid DESC
        LIMIT ?
        """,
        (limit,),
    )

    rows = cursor.fetchall()
    conn.close()

    return rows