from app.backend.db.sqlite_conn import SQLiteConnection
class GeneratedImagesRepository:
    def __init__(self, db_conn: SQLiteConnection):
        self.db_conn = db_conn
    
    def get_all_images(self):
        sql = """SELECT * FROM generated_images"""
        with self.db_conn.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(sql)
            return cursor.fetchall()

    def get_image_by_id(self, id):
        sql = """SELECT * FROM generated_images WHERE id = ?"""
        with self.db_conn.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (id,))
            cursor.fetchone()
