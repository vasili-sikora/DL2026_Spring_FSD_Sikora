import sqlite3
from pathlib import Path

import pytest

from app.backend.db.sqlite_conn import SQLiteConnection
from app.backend.repositories.generated_images_repo import GeneratedImagesRepository
from app.backend.repositories.templates_repo import TemplateRepository
from app.backend.repositories.user_repo import UserRepo
from app.backend.services.exceptions import UserAlreadyExistsError

SCHEMA_SQL = """
CREATE TABLE templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    image_path TEXT NOT NULL,
    top_text_x INTEGER,
    top_text_y INTEGER,
    top_text_width INTEGER,
    bottom_text_x INTEGER,
    bottom_text_y INTEGER,
    bottom_text_width INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE generated_images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    template_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    text_top TEXT,
    text_bottom TEXT,
    image_path TEXT NOT NULL,
    share_token TEXT UNIQUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (template_id) REFERENCES templates(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE,
    password TEXT NOT NULL,
    is_admin INTEGER DEFAULT 0
);
"""


@pytest.fixture
def sqlite_db(tmp_path: Path) -> SQLiteConnection:
    db = SQLiteConnection(tmp_path / "test.sqlite3")
    with db.get_conn() as conn:
        conn.executescript(SCHEMA_SQL)
    return db


def test_sqlite_connection_enables_fk_and_row_factory(
    sqlite_db: SQLiteConnection,
) -> None:
    with sqlite_db.get_conn() as conn:
        fk_enabled = conn.execute("PRAGMA foreign_keys;").fetchone()[0]
        row = conn.execute("SELECT 1 AS one").fetchone()

    assert fk_enabled == 1
    assert isinstance(row, sqlite3.Row)
    assert row["one"] == 1


def test_template_repository_crud(sqlite_db: SQLiteConnection) -> None:
    repo = TemplateRepository(sqlite_db)

    created = repo.create_template(
        {
            "name": "Мем😀",
            "image_path": "data/templates/кот.png",
            "top_text_x": 20,
            "top_text_y": 24,
            "top_text_width": 400,
            "bottom_text_x": 20,
            "bottom_text_y": 300,
            "bottom_text_width": 400,
        }
    )
    assert created is not None
    template_id = created["id"]

    loaded = repo.get_template_by_id(template_id)
    assert loaded is not None
    assert loaded["name"] == "Мем😀"
    assert loaded["top_text_width"] == 400

    updated_rows = repo.update_template(
        template_id,
        {"name": "Updated", "image_path": "data/templates/updated.jpg"},
    )
    assert updated_rows == 1

    updated = repo.get_template_by_id(template_id)
    assert updated is not None
    assert updated["name"] == "Updated"
    assert updated["image_path"] == "data/templates/updated.jpg"

    layout_updated = repo.update_template_layout(
        template_id,
        {
            "top_text_x": 10,
            "top_text_y": 12,
            "top_text_width": 320,
            "bottom_text_x": 15,
            "bottom_text_y": 240,
            "bottom_text_width": 300,
        },
    )
    assert layout_updated is not None
    assert layout_updated["bottom_text_width"] == 300

    all_rows = repo.get_all_templates()
    assert len(all_rows) == 1

    deleted_rows = repo.delete_template(template_id)
    assert deleted_rows == 1
    assert repo.get_template_by_id(template_id) is None


def test_generated_images_repository_crud_and_lookup(
    sqlite_db: SQLiteConnection,
) -> None:
    templates_repo = TemplateRepository(sqlite_db)
    generated_repo = GeneratedImagesRepository(sqlite_db)
    users_repo = UserRepo(sqlite_db)
    template = templates_repo.create_template(
        {
            "name": "Base",
            "image_path": "data/templates/base.jpg",
            "top_text_x": 20,
            "top_text_y": 24,
            "top_text_width": 400,
            "bottom_text_x": 20,
            "bottom_text_y": 300,
            "bottom_text_width": 400,
        }
    )
    user = users_repo.save_user("generated@example.com", "hash-1")
    assert template is not None
    assert user is not None

    created = generated_repo.create_image(
        {
            "template_id": template["id"],
            "user_id": user["id"],
            "text_top": "😀 TOP",
            "text_bottom": "BOTTOM 😺",
            "image_path": "data/generated_images/item.jpg",
            "share_token": "token-1",
        }
    )
    assert created is not None

    fetched_by_id = generated_repo.get_image_by_id(created["id"], user["id"])
    assert fetched_by_id is not None
    assert fetched_by_id["share_token"] == "token-1"

    fetched_by_token = generated_repo.get_image_by_share_token("token-1")
    assert fetched_by_token is not None
    assert fetched_by_token["id"] == created["id"]

    all_images = generated_repo.get_all_images(user["id"])
    assert len(all_images) == 1


def test_generated_images_repository_respects_foreign_key(
    sqlite_db: SQLiteConnection,
) -> None:
    repo = GeneratedImagesRepository(sqlite_db)

    with pytest.raises(sqlite3.IntegrityError):
        repo.create_image(
            {
                "template_id": 999999,
                "user_id": 999999,
                "text_top": "A",
                "text_bottom": "B",
                "image_path": "data/generated_images/bad.jpg",
                "share_token": "bad-token",
            }
        )


def test_user_repo_save_login_and_duplicate(sqlite_db: SQLiteConnection) -> None:
    repo = UserRepo(sqlite_db)

    created_user = repo.save_user("user@example.com", "hash-1")
    assert created_user["email"] == "user@example.com"
    assert created_user["is_admin"] == 0

    stored_hash = repo.get_password_by_email("user@example.com")
    assert stored_hash == "hash-1"

    logged = repo.login_user("user@example.com")
    assert logged is not None
    assert logged["id"] == created_user["id"]

    assert repo.login_user("missing@example.com") is None
    assert repo.get_password_by_email("missing@example.com") is None

    with pytest.raises(UserAlreadyExistsError, match="User already exists"):
        repo.save_user("user@example.com", "hash-2")


def test_user_repo_can_promote_existing_user_to_admin(
    sqlite_db: SQLiteConnection,
) -> None:
    repo = UserRepo(sqlite_db)
    created_user = repo.save_user("admin@example.com", "hash-1")

    updated_user = repo.set_admin_status(created_user["id"], True)

    assert updated_user is not None
    assert updated_user["is_admin"] == 1
    assert repo.get_user_by_email("admin@example.com") == updated_user
