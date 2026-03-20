import shutil
from io import BytesIO
from pathlib import Path
from typing import cast

import pytest
from PIL import Image

from app.backend.core.config import BASE_DIR
from app.backend.services.exceptions import TemplateValidationError
from app.backend.services.templates_service import TemplateService


class FakeTemplateRepository:
    def __init__(self) -> None:
        self.created_payload: dict[str, object] | None = None

    def create_template(self, template: dict[str, object]) -> dict[str, object]:
        self.created_payload = template
        return {
            "id": 1,
            "name": template["name"],
            "image_path": template["image_path"],
            "top_text_x": template.get("top_text_x"),
            "top_text_y": template.get("top_text_y"),
            "top_text_width": template.get("top_text_width"),
            "bottom_text_x": template.get("bottom_text_x"),
            "bottom_text_y": template.get("bottom_text_y"),
            "bottom_text_width": template.get("bottom_text_width"),
            "created_at": "2026-03-17T00:00:00",
        }

    def get_all_templates(self) -> list[dict[str, object]]:
        return [
            {
                "id": 1,
                "name": "Template 1",
                "image_path": "data/templates/one.png",
                "top_text_x": 20,
                "top_text_y": 24,
                "top_text_width": 300,
                "bottom_text_x": 20,
                "bottom_text_y": 220,
                "bottom_text_width": 300,
            },
            {
                "id": 2,
                "name": "Template 2",
                "image_path": "data/templates/two.jpg",
                "top_text_x": 20,
                "top_text_y": 24,
                "top_text_width": 300,
                "bottom_text_x": 20,
                "bottom_text_y": 220,
                "bottom_text_width": 300,
            },
        ]

    def get_template_by_id(self, template_id: int) -> dict[str, object] | None:
        if template_id == 1:
            return {
                "id": 1,
                "name": "Template 1",
                "image_path": "data/templates/one.png",
                "top_text_x": 20,
                "top_text_y": 24,
                "top_text_width": 300,
                "bottom_text_x": 20,
                "bottom_text_y": 220,
                "bottom_text_width": 300,
            }
        return None

    def update_template_layout(
        self, template_id: int, layout: dict[str, int]
    ) -> dict[str, object] | None:
        if template_id != 1:
            return None
        return {
            "id": 1,
            "name": "Template 1",
            "image_path": "data/templates/one.png",
            **layout,
        }


def test_create_template_rejects_empty_name() -> None:
    service = TemplateService(FakeTemplateRepository())

    with pytest.raises(TemplateValidationError, match="Template name required"):
        service.create_template({"name": "", "image_name": "meme.png"})


@pytest.mark.parametrize(
    "image_name",
    [
        "script.sh",
        "archive.zip",
        "vector.svg",
        "photo.webp",
        "memejpeg",
    ],
)
def test_create_template_rejects_non_image_formats(image_name: str) -> None:
    service = TemplateService(FakeTemplateRepository())

    with pytest.raises(TemplateValidationError, match="Incorrect file format"):
        service.create_template({"name": "Bad", "image_name": image_name})


def test_create_template_accepts_unicode_and_emoji_file_name() -> None:
    repo = FakeTemplateRepository()
    service = TemplateService(repo)

    result = service.create_template({"name": "Мем", "image_name": "кот😀.png"})

    assert result["id"] == 1
    assert repo.created_payload is not None
    assert repo.created_payload["image_path"] == "data/templates/кот😀.png"


def test_get_all_templates_passes_repository_result() -> None:
    service = TemplateService(FakeTemplateRepository())

    templates = service.get_all_templates()

    assert len(templates) == 2
    assert templates[0]["name"] == "Template 1"


def test_get_template_by_id_passes_repository_result() -> None:
    service = TemplateService(FakeTemplateRepository())

    found = service.get_template_by_id(1)
    missing = service.get_template_by_id(999)

    assert found is not None
    assert found["id"] == 1
    assert missing is None


def test_create_template_should_reject_path_traversal() -> None:
    service = TemplateService(FakeTemplateRepository())

    with pytest.raises(TemplateValidationError, match="must not contain directories"):
        service.create_template({"name": "Traversal", "image_name": "../../secret.png"})


def test_create_template_from_upload_saves_image_and_registers_template(
    monkeypatch: pytest.MonkeyPatch, tmp_path
) -> None:
    repo = FakeTemplateRepository()
    service = TemplateService(repo)

    upload_dir = BASE_DIR / ".tmp_test_template_uploads" / tmp_path.name
    upload_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(
        "app.backend.storage.template_storage.TEMPLATES_DIR", upload_dir
    )

    image_buffer = BytesIO()
    Image.new("RGB", (10, 10), "white").save(image_buffer, format="PNG")

    try:
        result = service.create_template_from_upload(
            name="Uploaded Template",
            image_name="my upload.png",
            image_content=image_buffer.getvalue(),
        )

        assert result["name"] == "Uploaded Template"
        assert repo.created_payload is not None
        saved_path = (
            upload_dir / Path(cast(str, repo.created_payload["image_path"])).name
        )
        assert saved_path.exists()
        assert repo.created_payload["top_text_width"] is not None
    finally:
        shutil.rmtree(upload_dir.parent, ignore_errors=True)
