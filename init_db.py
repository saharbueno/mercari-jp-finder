import sqlite3

conn = sqlite3.connect("data/listings.db")

cursor = conn.cursor()

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS keywords (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        keyword TEXT UNIQUE
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
        image TEXT
    )
"""
)

conn.commit()
conn.close()

print("Database initialized.")