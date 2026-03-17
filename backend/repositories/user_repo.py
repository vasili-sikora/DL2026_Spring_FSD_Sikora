from app.backend.db.sqlite_conn import SQLiteConnection


class UserRepo:
    def __init__(self, db_conn: SQLiteConnection):
        self._db_conn = db_conn

    def get_password_by_email(self, email: str) -> str | None:
        sql = """SELECT password FROM users WHERE email = ?"""
        with self._db_conn.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (email,))
            row = cursor.fetchone()

            return row["password"] if row else None

    def save_user(self, email: str, password: str) -> dict:
        sql = """INSERT INTO users (email, password) VALUES (?, ?)"""
        with self._db_conn.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (email, password))

            row_id = cursor.lastrowid
            cursor.execute(
                """SELECT id, email, is_admin FROM users WHERE id = ?""", (row_id,)
            )
            row = cursor.fetchone()
            return dict(row)

    def login_user(self, email: str) -> dict | None:
        sql = """SELECT id, email, is_admin FROM users WHERE email = ?"""

        with self._db_conn.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (email,))
            row = cursor.fetchone()

            return dict(row) if row else None
