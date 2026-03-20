from io import BytesIO
from pathlib import Path
from typing import Any, Iterator

import pytest
from fastapi import HTTPException, UploadFile
from pydantic import ValidationError
from slowapi.errors import RateLimitExceeded
from starlette.requests import Request
from starlette.responses import Response

from app.backend.api.auth_routes import get_me, login_user, logout_user, register_user
from app.backend.api.generated_images_routes import (
    generate_image,
    get_image_by_id,
    get_image_by_share_token,
    get_images,
    preview_image,
)
from app.backend.api.templates_routes import (
    create_template,
    get_template_by_id,
    get_template_image,
    get_templates,
    preview_template_layout,
    update_template_layout,
    upload_template,
)
from app.backend.core.rate_limit import limiter
from app.backend.models.generated_images import (
    GenerateImageRequest,
    PreviewImageRequest,
)
from app.backend.models.templates import (
    TemplateCreate,
    TemplateLayoutPreviewRequest,
    TemplateLayoutUpdate,
)
from app.backend.models.user import UserCreate, UserLogin
from app.backend.services.exceptions import (
    AuthenticationError,
    ImageGenerationValidationError,
    ImageNotFoundError,
    TemplateFontError,
    TemplateImageFileNotFoundError,
    TemplateImageFormatError,
    TemplateNotFoundError,
    TemplateValidationError,
    UserNotFoundError,
)


class _DummyApp:
    def __init__(self) -> None:
        self.state = type("State", (), {})()
        self.state.limiter = limiter


def make_request(
    method: str,
    path: str,
    ip: str = "127.0.0.1",
    port: int = 12345,
) -> Request:
    scope = {
        "type": "http",
        "method": method,
        "path": path,
        "headers": [],
        "client": (ip, port),
        "app": _DummyApp(),
    }
    return Request(scope)


@pytest.fixture(autouse=True)
def reset_rate_limiter() -> Iterator[None]:
    limiter.reset()
    yield
    limiter.reset()


def test_auth_register_maps_service_error_to_http_400(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class _ServiceFail:
        @staticmethod
        def register_user(payload: Any) -> dict[str, Any]:
            raise AuthenticationError("Invalid payload")

    monkeypatch.setattr("app.backend.api.auth_routes.service", _ServiceFail)

    response = Response()
    with pytest.raises(HTTPException) as exc_info:
        register_user(
            UserCreate(email="user@example.com", password="abcd1234"), response
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Invalid payload"


def test_auth_login_with_emoji_password_success(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class _ServiceOk:
        @staticmethod
        def login_user(payload: Any) -> dict[str, Any]:
            return {"id": 7, "email": payload.email, "is_admin": 0}

    monkeypatch.setattr("app.backend.api.auth_routes.service", _ServiceOk)

    response = Response()
    result = login_user(
        UserLogin(email="emoji.user@example.com", password="Пароль😀1234"),
        response,
    )

    assert result["id"] == 7
    assert result["email"] == "emoji.user@example.com"


def test_auth_me_returns_current_user(monkeypatch: pytest.MonkeyPatch) -> None:
    class _ServiceOk:
        @staticmethod
        def get_user_by_id(user_id: int) -> dict[str, Any]:
            return {"id": user_id, "email": "me@example.com", "is_admin": 0}

    monkeypatch.setattr("app.backend.api.auth_routes.service", _ServiceOk)

    result = get_me(5)

    assert result["id"] == 5
    assert result["email"] == "me@example.com"


def test_auth_me_maps_user_not_found_to_http_401(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class _ServiceFail:
        @staticmethod
        def get_user_by_id(_user_id: int) -> dict[str, Any]:
            raise UserNotFoundError("User not found")

    monkeypatch.setattr("app.backend.api.auth_routes.service", _ServiceFail)

    with pytest.raises(HTTPException) as exc_info:
        get_me(5)

    assert exc_info.value.status_code == 401


def test_auth_logout_returns_ok_message() -> None:
    response = Response()

    result = logout_user(response)

    assert result["detail"] == "Logged out"


def test_templates_list_and_get_by_id(monkeypatch: pytest.MonkeyPatch) -> None:
    class _TemplateService:
        @staticmethod
        def get_all_templates() -> list[dict[str, Any]]:
            return [
                {
                    "id": 1,
                    "name": "One",
                    "image_path": "data/templates/one.jpg",
                    "top_text_x": 20,
                    "top_text_y": 24,
                    "top_text_width": 300,
                    "bottom_text_x": 20,
                    "bottom_text_y": 220,
                    "bottom_text_width": 300,
                },
                {
                    "id": 2,
                    "name": "Two",
                    "image_path": "data/templates/two.jpg",
                    "top_text_x": 20,
                    "top_text_y": 24,
                    "top_text_width": 300,
                    "bottom_text_x": 20,
                    "bottom_text_y": 220,
                    "bottom_text_width": 300,
                },
            ]

        @staticmethod
        def get_template_by_id(template_id: int) -> dict[str, Any] | None:
            if template_id == 1:
                return {
                    "id": 1,
                    "name": "One",
                    "image_path": "data/templates/one.jpg",
                    "top_text_x": 20,
                    "top_text_y": 24,
                    "top_text_width": 300,
                    "bottom_text_x": 20,
                    "bottom_text_y": 220,
                    "bottom_text_width": 300,
                }
            return None

    monkeypatch.setattr(
        "app.backend.api.templates_routes.template_service", _TemplateService
    )

    all_templates = get_templates()
    assert len(all_templates) == 2

    found = get_template_by_id(1)
    assert found["id"] == 1

    with pytest.raises(HTTPException) as exc_info:
        get_template_by_id(999)
    assert exc_info.value.status_code == 404


def test_templates_create_maps_service_error(monkeypatch: pytest.MonkeyPatch) -> None:
    class _TemplateServiceFail:
        @staticmethod
        def create_template(payload: dict[str, Any]) -> dict[str, Any]:
            raise TemplateValidationError("Incorrect file format")

    monkeypatch.setattr(
        "app.backend.api.templates_routes.template_service", _TemplateServiceFail
    )

    with pytest.raises(HTTPException) as exc_info:
        create_template(
            TemplateCreate(name="Bad", image_name="archive.zip"),
            {"id": 1, "is_admin": 1},
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Incorrect file format"


def test_templates_image_returns_fileresponse(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    image_path = tmp_path / "template.jpg"
    image_path.write_bytes(b"fake-image")

    class _TemplateServiceImage:
        @staticmethod
        def get_template_by_id(template_id: int) -> dict[str, Any] | None:
            return {"id": 1, "name": "One", "image_path": str(image_path)}

    monkeypatch.setattr(
        "app.backend.api.templates_routes.template_service", _TemplateServiceImage
    )

    response = get_template_image(1)

    assert response.status_code == 200
    assert str(image_path) in str(response.path)


def test_upload_template_maps_service_error(monkeypatch: pytest.MonkeyPatch) -> None:
    class _TemplateServiceFail:
        @staticmethod
        def create_template_from_upload(
            name: str, image_name: str, image_content: bytes
        ) -> dict[str, Any]:
            raise TemplateValidationError("Incorrect file format")

    monkeypatch.setattr(
        "app.backend.api.templates_routes.template_service", _TemplateServiceFail
    )

    upload = UploadFile(filename="bad.txt", file=BytesIO(b"bad"))

    with pytest.raises(HTTPException) as exc_info:
        upload_template("Bad", upload, {"id": 1, "is_admin": 1})

    assert exc_info.value.status_code == 400


def test_update_template_layout_maps_not_found(monkeypatch: pytest.MonkeyPatch) -> None:
    class _TemplateServiceFail:
        @staticmethod
        def update_template_layout(
            template_id: int, payload: dict[str, Any]
        ) -> dict[str, Any]:
            raise TemplateValidationError("Template not found")

    monkeypatch.setattr(
        "app.backend.api.templates_routes.template_service", _TemplateServiceFail
    )

    with pytest.raises(HTTPException) as exc_info:
        update_template_layout(
            1,
            TemplateLayoutUpdate(
                top_text_x=10,
                top_text_y=10,
                top_text_width=200,
                bottom_text_x=10,
                bottom_text_y=200,
                bottom_text_width=200,
            ),
            {"id": 1, "is_admin": 1},
        )

    assert exc_info.value.status_code == 404


def test_preview_template_layout_maps_validation_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class _TemplateServiceFail:
        @staticmethod
        def preview_template_layout(**kwargs: Any) -> bytes:
            raise TemplateValidationError("Top text block exceeds image width")

    monkeypatch.setattr(
        "app.backend.api.templates_routes.template_service", _TemplateServiceFail
    )

    with pytest.raises(HTTPException) as exc_info:
        preview_template_layout(
            1,
            TemplateLayoutPreviewRequest(
                top_text_x=10,
                top_text_y=10,
                top_text_width=600,
                bottom_text_x=10,
                bottom_text_y=200,
                bottom_text_width=200,
            ),
            {"id": 1, "is_admin": 1},
        )

    assert exc_info.value.status_code == 400


def test_generated_list_maps_not_found(monkeypatch: pytest.MonkeyPatch) -> None:
    class _GeneratedServiceMissing:
        @staticmethod
        def get_all_images(_user_id: int) -> list[dict[str, Any]]:
            raise ImageNotFoundError("Images not found")

    monkeypatch.setattr(
        "app.backend.api.generated_images_routes.generated_images_service",
        _GeneratedServiceMissing,
    )

    with pytest.raises(HTTPException) as exc_info:
        get_images(1)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Images not found"


def test_generated_get_by_id_maps_not_found(monkeypatch: pytest.MonkeyPatch) -> None:
    class _GeneratedServiceMissingById:
        @staticmethod
        def get_image_by_id(image_id: int, _user_id: int) -> dict[str, Any]:
            raise ImageNotFoundError("Image not found")

    monkeypatch.setattr(
        "app.backend.api.generated_images_routes.generated_images_service",
        _GeneratedServiceMissingById,
    )

    with pytest.raises(HTTPException) as exc_info:
        get_image_by_id(999, 1)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Image not found"


@pytest.mark.parametrize(
    "exception_obj, expected_status",
    [
        (TemplateNotFoundError("Template not found"), 404),
        (TemplateImageFileNotFoundError("Template image file not found"), 404),
        (TemplateImageFormatError("Template image format is not supported"), 400),
        (TemplateFontError("Unsupported font"), 400),
    ],
)
def test_generate_maps_domain_errors(
    monkeypatch: pytest.MonkeyPatch,
    exception_obj: Exception,
    expected_status: int,
) -> None:
    class _GeneratedServiceError:
        @staticmethod
        def generate_image(
            template_id: int, payload: Any, _user_id: int
        ) -> dict[str, Any]:
            raise exception_obj

    monkeypatch.setattr(
        "app.backend.api.generated_images_routes.generated_images_service",
        _GeneratedServiceError,
    )

    request = make_request("POST", "/templates/1/generate")
    payload = GenerateImageRequest(
        text_top="😀 TOP",
        text_bottom="BOTTOM 😺",
        font_name="dejavu_sans",
        font_size=40,
        font_color="#ffffff",
    )

    with pytest.raises(HTTPException) as exc_info:
        generate_image.__wrapped__(request, 1, payload, 1)

    assert exc_info.value.status_code == expected_status


@pytest.mark.parametrize(
    "exception_obj, expected_status",
    [
        (TemplateNotFoundError("Template not found"), 404),
        (TemplateImageFileNotFoundError("Template image file not found"), 404),
        (TemplateImageFormatError("Template image format is not supported"), 400),
        (TemplateFontError("Unsupported font"), 400),
        (ImageGenerationValidationError("Invalid font size"), 400),
    ],
)
def test_preview_maps_errors(
    monkeypatch: pytest.MonkeyPatch,
    exception_obj: Exception,
    expected_status: int,
) -> None:
    class _GeneratedServiceError:
        @staticmethod
        def preview_image(template_id: int, payload: Any) -> bytes:
            raise exception_obj

    monkeypatch.setattr(
        "app.backend.api.generated_images_routes.generated_images_service",
        _GeneratedServiceError,
    )

    request = make_request("POST", "/templates/1/preview")
    payload = PreviewImageRequest(
        text_top="😀 TOP",
        text_bottom="BOTTOM 😺",
        font_name="dejavu_sans",
        font_size=40,
        font_color="#ffffff",
    )

    with pytest.raises(HTTPException) as exc_info:
        preview_image.__wrapped__(request, 1, payload)

    assert exc_info.value.status_code == expected_status


def test_preview_rate_limit_50_per_minute(monkeypatch: pytest.MonkeyPatch) -> None:
    class _GeneratedServiceOk:
        @staticmethod
        def preview_image(template_id: int, payload: Any) -> bytes:
            return b"jpeg-preview"

    monkeypatch.setattr(
        "app.backend.api.generated_images_routes.generated_images_service",
        _GeneratedServiceOk,
    )

    payload = PreviewImageRequest()
    for _ in range(50):
        request = make_request("POST", "/templates/1/preview", ip="10.0.0.1", port=5555)
        response = preview_image(request, 1, payload)
        assert response.status_code == 200

    request = make_request("POST", "/templates/1/preview", ip="10.0.0.1", port=5555)
    with pytest.raises(RateLimitExceeded):
        preview_image(request, 1, payload)


def test_generate_rate_limit_10_per_minute(monkeypatch: pytest.MonkeyPatch) -> None:
    class _GeneratedServiceOk:
        @staticmethod
        def generate_image(
            template_id: int, payload: Any, _user_id: int
        ) -> dict[str, Any]:
            return {
                "id": 1,
                "template_id": template_id,
                "text_top": payload.text_top,
                "text_bottom": payload.text_bottom,
                "image_path": "data/generated_images/new.jpg",
                "share_token": "tok-new",
                "created_at": "2026-03-17T00:00:00",
            }

    monkeypatch.setattr(
        "app.backend.api.generated_images_routes.generated_images_service",
        _GeneratedServiceOk,
    )

    payload = GenerateImageRequest()
    for _ in range(10):
        request = make_request(
            "POST", "/templates/1/generate", ip="10.0.0.2", port=6666
        )
        response = generate_image(request, 1, payload, 1)
        assert response.id == 1

    request = make_request("POST", "/templates/1/generate", ip="10.0.0.2", port=6666)
    with pytest.raises(RateLimitExceeded):
        generate_image(request, 1, payload, 1)


def test_share_token_maps_not_found(monkeypatch: pytest.MonkeyPatch) -> None:
    class _GeneratedServiceMissingToken:
        @staticmethod
        def get_image_by_share_token(share_token: str) -> dict[str, Any]:
            raise ImageNotFoundError("Image not found")

    monkeypatch.setattr(
        "app.backend.api.generated_images_routes.generated_images_service",
        _GeneratedServiceMissingToken,
    )

    with pytest.raises(HTTPException) as exc_info:
        get_image_by_share_token("missing")

    assert exc_info.value.status_code == 404


def test_share_token_returns_file(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    image_path = tmp_path / "generated.jpg"
    image_path.write_bytes(b"binary-image")

    class _GeneratedServiceOk:
        @staticmethod
        def get_image_by_share_token(share_token: str) -> dict[str, Any]:
            return {"image_path": str(image_path)}

    monkeypatch.setattr(
        "app.backend.api.generated_images_routes.generated_images_service",
        _GeneratedServiceOk,
    )

    response = get_image_by_share_token("token")

    assert response.status_code == 200
    assert str(image_path) in str(response.path)


def test_preview_payload_validation_rejects_small_font() -> None:
    with pytest.raises(ValidationError):
        PreviewImageRequest(font_size=1)
