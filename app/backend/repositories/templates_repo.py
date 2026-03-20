import sqlite3
from typing import Any, Mapping

from app.backend.db.sqlite_conn import SQLiteConnection

TemplatePayload = Mapping[str, Any]


class TemplateRepository:
    def __init__(self, db_conn: SQLiteConnection) -> None:
        self.db_conn = db_conn

    def create_template(self, template: TemplatePayload) -> sqlite3.Row | None:
        sql = """
        INSERT INTO templates (
            name,
            image_path,
            top_text_x,
            top_text_y,
            top_text_width,
            bottom_text_x,
            bottom_text_y,
            bottom_text_width
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        with self.db_conn.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                sql,
                (
                    template["name"],
                    template["image_path"],
                    template.get("top_text_x"),
                    template.get("top_text_y"),
                    template.get("top_text_width"),
                    template.get("bottom_text_x"),
                    template.get("bottom_text_y"),
                    template.get("bottom_text_width"),
                ),
            )

            cursor.execute(
                """
                        SELECT id, name, image_path,
                               top_text_x, top_text_y, top_text_width,
                               bottom_text_x, bottom_text_y, bottom_text_width,
                               created_at
                        FROM templates
                        WHERE id = ?
                        """,
                (cursor.lastrowid,),
            )

            return cursor.fetchone()

    def get_template_by_id(self, template_id: int) -> sqlite3.Row | None:
        sql = """
        SELECT id, name, image_path,
               top_text_x, top_text_y, top_text_width,
               bottom_text_x, bottom_text_y, bottom_text_width,
               created_at
        FROM templates
        WHERE id = ?
        """
        with self.db_conn.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (template_id,))
            return cursor.fetchone()

    def update_template(self, template_id: int, template: TemplatePayload) -> int:
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

    def delete_template(self, template_id: int) -> int:
        sql = """DELETE FROM templates WHERE id = ?"""
        with self.db_conn.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (template_id,))
            return cursor.rowcount

    def update_template_layout(
        self, template_id: int, layout: TemplatePayload
    ) -> sqlite3.Row | None:
        sql = """
        UPDATE templates
        SET top_text_x = ?,
            top_text_y = ?,
            top_text_width = ?,
            bottom_text_x = ?,
            bottom_text_y = ?,
            bottom_text_width = ?
        WHERE id = ?
        """
        with self.db_conn.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                sql,
                (
                    layout["top_text_x"],
                    layout["top_text_y"],
                    layout["top_text_width"],
                    layout["bottom_text_x"],
                    layout["bottom_text_y"],
                    layout["bottom_text_width"],
                    template_id,
                ),
            )
            if cursor.rowcount != 1:
                return None

            cursor.execute(
                """
                SELECT id, name, image_path,
                       top_text_x, top_text_y, top_text_width,
                       bottom_text_x, bottom_text_y, bottom_text_width,
                       created_at
                FROM templates
                WHERE id = ?
                """,
                (template_id,),
            )
            return cursor.fetchone()

    def get_all_templates(self) -> list[sqlite3.Row]:
        sql = """
        SELECT id, name, image_path,
               top_text_x, top_text_y, top_text_width,
               bottom_text_x, bottom_text_y, bottom_text_width,
               created_at
        FROM templates
        """
        with self.db_conn.get_conn() as conn:
            cursor = conn.execute(sql)
            return cursor.fetchall()
