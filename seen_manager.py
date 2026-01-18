import sqlite3
import time

DB_PATH = "seen.db"
KEEP_DAYS = 7
KEEP_SECONDS = KEEP_DAYS * 24 * 60 * 60


def init_db():
    """seen.db が無い場合は自動生成し、テーブルを作成する"""
    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS seen (
                item_id TEXT PRIMARY KEY,
                timestamp REAL
            )
        """)
        conn.commit()
    finally:
        conn.close()


def load_seen_ids():
    """既に通知済みの item_id をセットで返す"""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.cursor()
        cur.execute("SELECT item_id FROM seen")
        rows = cur.fetchall()
        return {row[0] for row in rows}
    finally:
        conn.close()


def mark_seen(item_id):
    """通知済みとして item_id を登録する"""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT OR REPLACE INTO seen (item_id, timestamp) VALUES (?, ?)",
            (item_id, time.time())
        )
        conn.commit()
    finally:
        conn.close()


def cleanup_old_entries():
    """1週間より古い item_id を削除し、削除件数を返す"""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.cursor()
        limit = time.time() - KEEP_SECONDS
        cur.execute("DELETE FROM seen WHERE timestamp < ?", (limit,))
        deleted = cur.rowcount
        conn.commit()
        return deleted
    finally:
        conn.close()
