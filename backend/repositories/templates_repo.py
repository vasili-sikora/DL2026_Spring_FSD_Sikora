from app.backend.core.config import TEMPLATES_DIR
from app.backend.db.sqlite_conn import SQLiteConnection


class TemplateRepository:
    def __init__(self, db_conn: SQLiteConnection):
        self.db_conn = db_conn

    def create_template(self, template):
        sql = """INSERT INTO templates (name, image_path) VALUES (?, ?)"""
        with self.db_conn.get_conn() as conn:
            path = f"{TEMPLATES_DIR}/{template['image_name']}"

            cursor = conn.cursor()
            cursor.execute(sql, (template["name"], path))

            cursor.execute(
                """
                        SELECT id, name, image_path, created_at
                        FROM templates
                        WHERE id = ?
                        """,
                (cursor.lastrowid,),
            )

            return cursor.fetchone()

    def get_template_by_id(self, template_id):
        sql = """SELECT id, name, image_path, created_at FROM templates WHERE id = ?"""
        with self.db_conn.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (template_id,))
            return cursor.fetchone()

    def update_template(self, template_id, template):
        sql = """UPDATE templates SET name = ?, image_path = ? WHERE id = ?"""
        with self.db_conn.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                sql,
                (
                    template["name"],
                    template["image_path"],
                    template_id,
                ),
            )
            return cursor.rowcount

    def delete_template(self, template_id):
        sql = """DELETE FROM templates WHERE id = ?"""
        with self.db_conn.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (template_id,))
            return cursor.rowcount

    def get_all_templates(self):
        sql = """SELECT id, name, image_path, created_at FROM templates"""
        with self.db_conn.get_conn() as conn:
            cursor = conn.execute(sql)
            return cursor.fetchall()
