from app.backend.db.sqlite_conn import SQLiteConnection


class GeneratedImagesRepository:
    def __init__(self, db_conn: SQLiteConnection):
        self.db_conn = db_conn

    def create_image(self, image):
        sql = """
        INSERT INTO generated_images (template_id, text_top, text_bottom, image_path, share_token)
        VALUES (?, ?, ?, ?, ?)
        """
        with self.db_conn.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                sql,
                (
                    image["template_id"],
                    image["text_top"],
                    image["text_bottom"],
                    image["image_path"],
                    image["share_token"],
                ),
            )
            cursor.execute(
                """
                SELECT id, template_id, text_top, text_bottom, image_path, share_token, created_at
                FROM generated_images
                WHERE id = ?
                """,
                (cursor.lastrowid,),
            )
            return cursor.fetchone()

    def get_all_images(self):
        sql = """SELECT * FROM generated_images"""
        with self.db_conn.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(sql)
            return cursor.fetchall()

    def get_image_by_id(self, image_id: int):
        sql = """SELECT * FROM generated_images WHERE id = ?"""
        with self.db_conn.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (image_id,))
            return cursor.fetchone()

    def get_image_by_share_token(self, share_token: str):
        sql = """
        SELECT id, template_id, text_top, text_bottom, image_path, share_token, created_at
        FROM generated_images
        WHERE share_token = ?
        """
        with self.db_conn.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (share_token,))
            return cursor.fetchone()
