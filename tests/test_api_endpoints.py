import pytest
from fastapi import HTTPException

from app.backend.api.generated_images_routes import get_images
from app.backend.api.templates_routes import get_template_by_id
from app.backend.services.exceptions import ImageNotFoundError


class _TemplateServiceMissing:
    @staticmethod
    def get_template_by_id(_template_id):
        return None


class _TemplateServiceFound:
    @staticmethod
    def get_template_by_id(_template_id):
        return {"id": 1, "name": "Template", "image_path": "data/templates/images.png"}


class _GeneratedImagesServiceMissing:
    @staticmethod
    def get_all_images(_user_id):
        raise ImageNotFoundError("Images not found")


class _GeneratedImagesServiceFound:
    @staticmethod
    def get_all_images(_user_id):
        return [{"id": 1, "template_id": 1, "share_token": "abc"}]


def test_get_template_by_id_returns_404_when_missing(monkeypatch):
    monkeypatch.setattr(
        "app.backend.api.templates_routes.template_service", _TemplateServiceMissing
    )

    with pytest.raises(HTTPException) as exc_info:
        get_template_by_id(999)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Template not found"


def test_get_template_by_id_returns_template_when_found(monkeypatch):
    monkeypatch.setattr(
        "app.backend.api.templates_routes.template_service", _TemplateServiceFound
    )

    result = get_template_by_id(1)

    assert result["id"] == 1
    assert result["name"] == "Template"


def test_get_images_returns_404_when_empty_service_error(monkeypatch):
    monkeypatch.setattr(
        "app.backend.api.generated_images_routes.generated_images_service",
        _GeneratedImagesServiceMissing,
    )

    with pytest.raises(HTTPException) as exc_info:
        get_images(1)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Images not found"


def test_get_images_returns_list_on_success(monkeypatch):
    monkeypatch.setattr(
        "app.backend.api.generated_images_routes.generated_images_service",
        _GeneratedImagesServiceFound,
    )

    result = get_images(1)

    assert len(result) == 1
    assert result[0]["id"] == 1
