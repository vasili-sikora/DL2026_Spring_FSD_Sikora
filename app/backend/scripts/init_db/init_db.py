from pathlib import Path

from app.backend.db.sqlite_conn import SQLiteConnection


def main() -> None:
    sql_path = Path(__file__).with_name("init_db.sql")
    conn = SQLiteConnection().get_conn()
    with sql_path.open(encoding="utf-8") as f:
        conn.executescript(f.read())
    conn.close()


if __name__ == "__main__":
    main()
