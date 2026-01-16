import sqlite3
import time
import os

DB_PATH = "seen.db"
KEEP_DAYS = 7
KEEP_SECONDS = KEEP_DAYS * 24 * 60 * 60


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS seen (
            item_id TEXT PRIMARY KEY,
            timestamp REAL
        )
    """)
    conn.commit()
    conn.close()


def load_seen_ids():
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT item_id FROM seen")
    rows = cur.fetchall()

    conn.close()
    return {row[0] for row in rows}


def mark_seen(item_id):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute(
        "INSERT OR REPLACE INTO seen (item_id, timestamp) VALUES (?, ?)",
        (item_id, time.time())
    )

    conn.commit()
    conn.close()


def cleanup_old_entries():
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    limit = time.time() - KEEP_SECONDS

    cur.execute("DELETE FROM seen WHERE timestamp < ?", (limit,))
    deleted = cur.rowcount

    conn.commit()
    conn.close()

    return deleted
