from pathlib import Path
from typing import Any

import pytest

from app.backend.core.config import BASE_DIR
from app.backend.models.generated_images import (
    GenerateImageRequest,
    PreviewImageRequest,
)
from app.backend.services.exceptions import (
    ImageGenerationValidationError,
    ImageNotFoundError,
    InvalidUserContextError,
    TemplateFontError,
    TemplateImageFileNotFoundError,
    TemplateImageFormatError,
    TemplateNotFoundError,
)
from app.backend.services.generated_images_service import GeneratedImagesService
from app.backend.utils.image_generation import (
    TemplateFontReadError,
    TemplateImageReadError,
)


class FakeGeneratedImagesRepository:
    def __init__(self) -> None:
        self.created_payload: dict[str, Any] | None = None
        self.images: list[dict[str, Any]] = []
        self.image_by_id: dict[int, dict[str, Any]] = {}
        self.image_by_token: dict[str, dict[str, Any]] = {}

    def create_image(self, image: dict[str, Any]) -> dict[str, Any]:
        self.created_payload = image
        return {
            "id": 11,
            "template_id": image["template_id"],
            "text_top": image["text_top"],
            "text_bottom": image["text_bottom"],
            "image_path": image["image_path"],
            "share_token": image["share_token"],
            "created_at": "2026-03-17T00:00:00",
        }

    def get_all_images(self, _user_id: int) -> list[dict[str, Any]]:
        return self.images

    def get_image_by_id(self, image_id: int, _user_id: int) -> dict[str, Any] | None:
        return self.image_by_id.get(image_id)

    def get_image_by_share_token(self, share_token: str) -> dict[str, Any] | None:
        return self.image_by_token.get(share_token)


class FakeTemplateRepository:
    def __init__(self, template: dict[str, Any] | None) -> None:
        self.template = template

    def get_template_by_id(self, template_id: int) -> dict[str, Any] | None:
        if template_id <= 0:
            return None
        return self.template


def test_get_all_images_returns_empty_list_without_error() -> None:
    images_repo = FakeGeneratedImagesRepository()
    service = GeneratedImagesService(images_repo, FakeTemplateRepository(None))

    result = service.get_all_images(1)

    assert result == []


def test_get_image_by_id_raises_when_missing() -> None:
    service = GeneratedImagesService(
        FakeGeneratedImagesRepository(), FakeTemplateRepository(None)
    )

    with pytest.raises(ImageNotFoundError, match="Image not found"):
        service.get_image_by_id(404, 1)


def test_generate_image_raises_when_template_missing() -> None:
    service = GeneratedImagesService(
        FakeGeneratedImagesRepository(),
        FakeTemplateRepository(None),
    )

    with pytest.raises(TemplateNotFoundError, match="Template not found"):
        service.generate_image(1, GenerateImageRequest(), 1)


def test_generate_image_raises_when_template_file_missing(tmp_path: Path) -> None:
    missing_file = tmp_path / "missing.jpg"
    service = GeneratedImagesService(
        FakeGeneratedImagesRepository(),
        FakeTemplateRepository({"id": 1, "image_path": str(missing_file)}),
    )

    with pytest.raises(
        TemplateImageFileNotFoundError, match="Template image file not found"
    ):
        service.generate_image(1, GenerateImageRequest(), 1)


def test_generate_image_maps_template_image_read_error(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    template_file = tmp_path / "template.jpg"
    template_file.write_bytes(b"stub")
    service = GeneratedImagesService(
        FakeGeneratedImagesRepository(),
        FakeTemplateRepository({"id": 1, "image_path": str(template_file)}),
    )

    def fake_render_generated_image(**kwargs: Any) -> tuple[str, Path]:
        raise TemplateImageReadError

    monkeypatch.setattr(
        "app.backend.services.generated_images_service.render_generated_image",
        fake_render_generated_image,
    )

    with pytest.raises(
        TemplateImageFormatError, match="Template image format is not supported"
    ):
        service.generate_image(1, GenerateImageRequest(), 1)


def test_generate_image_maps_font_read_error(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    template_file = tmp_path / "template.jpg"
    template_file.write_bytes(b"stub")
    service = GeneratedImagesService(
        FakeGeneratedImagesRepository(),
        FakeTemplateRepository({"id": 1, "image_path": str(template_file)}),
    )

    def fake_render_generated_image(**kwargs: Any) -> tuple[str, Path]:
        raise TemplateFontReadError("Unsupported font")

    monkeypatch.setattr(
        "app.backend.services.generated_images_service.render_generated_image",
        fake_render_generated_image,
    )

    with pytest.raises(TemplateFontError, match="Unsupported font"):
        service.generate_image(1, GenerateImageRequest(font_name="broken_font"), 1)


def test_generate_image_success_builds_relative_storage_path(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    template_file = tmp_path / "template.jpg"
    template_file.write_bytes(b"stub")
    images_repo = FakeGeneratedImagesRepository()
    service = GeneratedImagesService(
        images_repo,
        FakeTemplateRepository({"id": 1, "image_path": str(template_file)}),
    )

    def fake_render_generated_image(**kwargs: Any) -> tuple[str, Path]:
        return "token123", BASE_DIR / "data" / "generated_images" / "token123.jpg"

    monkeypatch.setattr(
        "app.backend.services.generated_images_service.render_generated_image",
        fake_render_generated_image,
    )

    payload = GenerateImageRequest(text_top="TOP", text_bottom="BOTTOM")
    result = service.generate_image(1, payload, 7)

    assert result["share_token"] == "token123"
    assert images_repo.created_payload is not None
    assert (
        images_repo.created_payload["image_path"]
        == "data/generated_images/token123.jpg"
    )
    assert images_repo.created_payload["user_id"] == 7


def test_preview_image_rejects_invalid_font_size_even_if_payload_is_untrusted() -> None:
    service = GeneratedImagesService(
        FakeGeneratedImagesRepository(),
        FakeTemplateRepository(
            {"id": 1, "image_path": str(BASE_DIR / "data" / "templates" / "x.jpg")}
        ),
    )
    untrusted_payload = PreviewImageRequest.model_construct(
        text_top="",
        text_bottom="",
        font_name="dejavu_sans",
        font_size=999,
    )

    with pytest.raises(ImageGenerationValidationError, match="Invalid font size"):
        service.preview_image(1, untrusted_payload)


def test_preview_image_accepts_emoji_text_and_returns_jpeg_bytes(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    template_file = tmp_path / "template.jpg"
    template_file.write_bytes(b"stub")
    service = GeneratedImagesService(
        FakeGeneratedImagesRepository(),
        FakeTemplateRepository({"id": 1, "image_path": str(template_file)}),
    )
    captured: dict[str, Any] = {}

    def fake_preview(**kwargs: Any) -> bytes:
        captured.update(kwargs)
        return b"jpeg-bytes"

    monkeypatch.setattr(
        "app.backend.services.generated_images_service.render_preview_image_bytes",
        fake_preview,
    )

    payload = PreviewImageRequest(text_top="😀 верх", text_bottom="нижний блок 😺")
    result = service.preview_image(1, payload)

    assert result == b"jpeg-bytes"
    assert captured["text_top"] == "😀 верх"
    assert captured["text_bottom"] == "нижний блок 😺"


def test_get_image_by_share_token_raises_when_missing() -> None:
    service = GeneratedImagesService(
        FakeGeneratedImagesRepository(), FakeTemplateRepository(None)
    )

    with pytest.raises(ImageNotFoundError, match="Image not found"):
        service.get_image_by_share_token("missing-token")


def test_get_all_images_rejects_invalid_user_id() -> None:
    service = GeneratedImagesService(
        FakeGeneratedImagesRepository(), FakeTemplateRepository(None)
    )

    with pytest.raises(InvalidUserContextError, match="Invalid user id"):
        service.get_all_images(0)
