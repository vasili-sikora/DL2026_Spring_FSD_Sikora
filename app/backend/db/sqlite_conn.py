import sqlite3
from pathlib import Path

from app.backend.core.config import (
    DB_PATH,
    SQLITE_BUSY_TIMEOUT_MS,
    SQLITE_ENABLE_WAL,
    SQLITE_SYNCHRONOUS,
)


class SQLiteConnection:
    def __init__(self, db_path: str | Path | None = None) -> None:
        self.db_path = Path(db_path) if db_path else DB_PATH

    def get_conn(self) -> sqlite3.Connection:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute(f"PRAGMA busy_timeout = {SQLITE_BUSY_TIMEOUT_MS};")
        if SQLITE_ENABLE_WAL:
            conn.execute("PRAGMA journal_mode = WAL;")
        conn.execute(f"PRAGMA synchronous = {SQLITE_SYNCHRONOUS};")
        conn.execute("PRAGMA temp_store = MEMORY;")
        conn.row_factory = sqlite3.Row
        return conn
