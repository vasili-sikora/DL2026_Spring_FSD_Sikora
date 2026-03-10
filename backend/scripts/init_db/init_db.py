from app.backend.db.sqlite_conn import SQLiteConnection

conn = SQLiteConnection().get_conn()

with open("app/backend/scripts/init_db/init_db.sql") as f:
    conn.executescript(f.read())

conn.close()
