from app.backend.db.sqlite_conn import SQLiteConnection


def main() -> None:
    conn = SQLiteConnection().get_conn()
    with open("app/backend/scripts/init_db/init_db.sql", encoding="utf-8") as f:
        conn.executescript(f.read())
    conn.close()


if __name__ == "__main__":
    main()
