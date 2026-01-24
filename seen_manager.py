import sqlite3
import time


class SeenManager:
    def __init__(self, db_path="seen.db"):
        self.db_path = db_path
        self.keep_seconds = 7 * 24 * 60 * 60
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
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

    def exists(self, item_id):
        conn = sqlite3.connect(self.db_path)
        try:
            cur = conn.cursor()
            cur.execute("SELECT 1 FROM seen WHERE item_id = ?", (item_id,))
            return cur.fetchone() is not None
        finally:
            conn.close()

    def add(self, item_id):
        conn = sqlite3.connect(self.db_path)
        try:
            cur = conn.cursor()
            cur.execute(
                "INSERT OR REPLACE INTO seen (item_id, timestamp) VALUES (?, ?)",
                (item_id, time.time())
            )
            conn.commit()
        finally:
            conn.close()

    def count(self):
        conn = sqlite3.connect(self.db_path)
        try:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM seen")
            return cur.fetchone()[0]
        finally:
            conn.close()

    def cleanup_old_entries(self, days=7):
        limit = time.time() - days * 24 * 60 * 60
        conn = sqlite3.connect(self.db_path)
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM seen WHERE timestamp < ?", (limit,))
            deleted = cur.rowcount
            conn.commit()
            return deleted
        finally:
            conn.close()
