from app.backend.core.config import DB_PATH
import sqlite3
from pathlib import Path

class SQLiteConnection:
    def __init__(self, db_path=None):
        self.db_path = Path(db_path) if db_path else DB_PATH

    def get_conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.row_factory = sqlite3.Row
        return conn
