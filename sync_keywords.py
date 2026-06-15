from pathlib import Path

from database import add_keyword, delete_keyword, get_keywords

KEYWORDS_FILE = Path("keywords.txt")


def load_keywords_from_file():
    if not KEYWORDS_FILE.exists():
        return []

    keywords = []

    for line in KEYWORDS_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()

        if line and not line.startswith("#"):
            keywords.append(line.strip())

    return keywords


def sync_keywords_from_file():
    file_keywords = load_keywords_from_file()
    db_keywords = set(get_keywords())
    file_set = set(file_keywords)

    added = []
    for keyword in file_keywords:
        if keyword not in db_keywords:
            add_keyword(keyword)
            added.append(keyword)

    removed = []
    for keyword in db_keywords:
        if keyword not in file_set:
            delete_keyword(keyword)
            removed.append(keyword)

    return added, removed
