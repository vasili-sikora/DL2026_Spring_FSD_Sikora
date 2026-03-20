import pytest

from app.backend.services.exceptions import TemplateValidationError
from app.backend.services.templates_service import TemplateService


class FakeTemplateRepository:
    def __init__(self) -> None:
        self.created_payload: dict[str, str] | None = None

    def create_template(self, template: dict[str, str]) -> dict[str, object]:
        self.created_payload = template
        return {
            "id": 1,
            "name": template["name"],
            "image_path": template["image_path"],
            "created_at": "2026-03-17T00:00:00",
        }

    def get_all_templates(self) -> list[dict[str, object]]:
        return [
            {"id": 1, "name": "Template 1", "image_path": "data/templates/one.png"},
            {"id": 2, "name": "Template 2", "image_path": "data/templates/two.jpg"},
        ]

    def get_template_by_id(self, template_id: int) -> dict[str, object] | None:
        if template_id == 1:
            return {
                "id": 1,
                "name": "Template 1",
                "image_path": "data/templates/one.png",
            }
        return None


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
