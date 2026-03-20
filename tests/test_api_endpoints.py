from io import BytesIO

import pytest
from fastapi import HTTPException
from starlette.datastructures import UploadFile
from starlette.responses import Response

from app.backend.api.generated_images_routes import get_images
from app.backend.api.templates_routes import (
    get_template_by_id,
    preview_template_layout,
    update_template_layout,
    upload_template,
)
from app.backend.models.templates import (
    TemplateLayoutPreviewRequest,
    TemplateLayoutUpdate,
)
from app.backend.services.exceptions import ImageNotFoundError


class _TemplateServiceMissing:
    @staticmethod
    def get_template_by_id(_template_id):
        return None


class _TemplateServiceFound:
    @staticmethod
    def get_template_by_id(_template_id):
        return {
            "id": 1,
            "name": "Template",
            "image_path": "data/templates/images.png",
            "top_text_x": 20,
            "top_text_y": 24,
            "top_text_width": 300,
            "bottom_text_x": 20,
            "bottom_text_y": 220,
            "bottom_text_width": 300,
        }


class _TemplateServiceUpload:
    @staticmethod
    def create_template_from_upload(name, image_name, image_content):
        return {
            "id": 3,
            "name": name,
            "image_path": f"data/templates/{image_name}",
            "created_at": "2026-03-21 12:00:00",
        }


class _TemplateServiceLayout:
    @staticmethod
    def update_template_layout(_template_id, payload):
        return {"id": 1, "name": "Template", **payload}

    @staticmethod
    def preview_template_layout(**_kwargs):
        return b"jpeg-preview"


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


def test_upload_template_returns_created_template(monkeypatch):
    monkeypatch.setattr(
        "app.backend.api.templates_routes.template_service", _TemplateServiceUpload
    )

    upload = UploadFile(filename="black.jpg", file=BytesIO(b"fake-image"))

    result = upload_template("Black", upload, {"id": 1, "is_admin": 1})

    assert result["id"] == 3
    assert result["name"] == "Black"


def test_update_template_layout_returns_updated_template(monkeypatch):
    monkeypatch.setattr(
        "app.backend.api.templates_routes.template_service", _TemplateServiceLayout
    )

    result = update_template_layout(
        1,
        TemplateLayoutUpdate(
            top_text_x=10,
            top_text_y=20,
            top_text_width=300,
            bottom_text_x=12,
            bottom_text_y=200,
            bottom_text_width=280,
        ),
        {"id": 1, "is_admin": 1},
    )

    assert result["top_text_width"] == 300


def test_preview_template_layout_returns_image_response(monkeypatch):
    monkeypatch.setattr(
        "app.backend.api.templates_routes.template_service", _TemplateServiceLayout
    )

    response = preview_template_layout(
        1,
        TemplateLayoutPreviewRequest(
            top_text_x=10,
            top_text_y=20,
            top_text_width=300,
            bottom_text_x=12,
            bottom_text_y=200,
            bottom_text_width=280,
            sample_text_top="TOP",
            sample_text_bottom="BOTTOM",
            font_name="dejavu_sans",
            font_size=40,
            font_color="#ffffff",
        ),
        {"id": 1, "is_admin": 1},
    )

    assert isinstance(response, Response)
    assert response.media_type == "image/jpeg"


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
