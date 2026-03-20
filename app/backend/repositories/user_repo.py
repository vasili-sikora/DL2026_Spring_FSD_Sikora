from sqlite3 import IntegrityError
from typing import Any

from app.backend.db.sqlite_conn import SQLiteConnection
from app.backend.services.exceptions import UserAlreadyExistsError


class UserRepo:
    def __init__(self, db_conn: SQLiteConnection) -> None:
        self._db_conn = db_conn

    def get_password_by_email(self, email: str) -> str | None:
        sql = """SELECT password FROM users WHERE email = ?"""
        with self._db_conn.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (email,))
            row = cursor.fetchone()

            return row["password"] if row else None

    def save_user(self, email: str, password: str) -> dict[str, Any]:
        sql = """INSERT INTO users (email, password) VALUES (?, ?)"""
        try:
            with self._db_conn.get_conn() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, (email, password))

                row_id = cursor.lastrowid
                cursor.execute(
                    """SELECT id, email, is_admin FROM users WHERE id = ?""", (row_id,)
                )
                row = cursor.fetchone()
                if not row:
                    raise UserAlreadyExistsError("Failed to load created user")
                return dict(row)
        except IntegrityError:
            raise UserAlreadyExistsError("User already exists")

    def login_user(self, email: str) -> dict[str, Any] | None:
        sql = """SELECT id, email, is_admin FROM users WHERE email = ?"""

        with self._db_conn.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (email,))
            row = cursor.fetchone()

            return dict(row) if row else None

    def get_user_by_email(self, email: str) -> dict[str, Any] | None:
        sql = """SELECT id, email, is_admin FROM users WHERE email = ?"""

        with self._db_conn.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (email,))
            row = cursor.fetchone()

            return dict(row) if row else None

    def get_user_by_id(self, user_id: int) -> dict[str, Any] | None:
        sql = """SELECT id, email, is_admin FROM users WHERE id = ?"""

        with self._db_conn.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (user_id,))
            row = cursor.fetchone()

            return dict(row) if row else None

    def set_admin_status(self, user_id: int, is_admin: bool) -> dict[str, Any] | None:
        sql = """UPDATE users SET is_admin = ? WHERE id = ?"""

        with self._db_conn.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (1 if is_admin else 0, user_id))
            if cursor.rowcount != 1:
                return None

            cursor.execute(
                """SELECT id, email, is_admin FROM users WHERE id = ?""", (user_id,)
            )
            row = cursor.fetchone()

            return dict(row) if row else None
