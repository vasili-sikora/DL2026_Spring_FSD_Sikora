from typing import Any

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from starlette.responses import FileResponse, Response

from app.backend.auth.dependencies import require_admin
from app.backend.dependencies import template_service
from app.backend.models.templates import (
    TemplateCreate,
    TemplateLayoutPreviewRequest,
    TemplateLayoutUpdate,
)
from app.backend.services.exceptions import TemplateValidationError
from app.backend.storage.paths import resolve_storage_path

templates_router: APIRouter = APIRouter()


@templates_router.get("/templates")
def get_templates() -> list[dict[str, Any]]:
    templates = template_service.get_all_templates()

    return [dict(template) for template in templates]


@templates_router.get("/templates/{template_id}")
def get_template_by_id(template_id: int) -> dict[str, Any]:
    template = template_service.get_template_by_id(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return dict(template)


@templates_router.get("/templates/{template_id}/image")
def get_template_image(template_id: int) -> FileResponse:
    template = template_service.get_template_by_id(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    resolved_path = resolve_storage_path(template["image_path"])

    if not resolved_path.exists():
        raise HTTPException(status_code=404, detail="Template image file not found")

    return FileResponse(resolved_path)


@templates_router.post("/templates")
def create_template(
    payload: TemplateCreate,
    _admin_user: dict[str, Any] = Depends(require_admin),
) -> dict[str, Any]:
    try:
        template = template_service.create_template(payload.model_dump())
    except TemplateValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return dict(template)


@templates_router.post("/admin/templates/upload")
def upload_template(
    name: str = Form(...),
    image: UploadFile = File(...),
    _admin_user: dict[str, Any] = Depends(require_admin),
) -> dict[str, Any]:
    try:
        template = template_service.create_template_from_upload(
            name=name.strip(),
            image_name=image.filename or "",
            image_content=image.file.read(),
        )
    except TemplateValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    finally:
        image.file.close()

    return dict(template)


@templates_router.patch("/admin/templates/{template_id}/layout")
def update_template_layout(
    template_id: int,
    payload: TemplateLayoutUpdate,
    _admin_user: dict[str, Any] = Depends(require_admin),
) -> dict[str, Any]:
    try:
        template = template_service.update_template_layout(
            template_id, payload.model_dump()
        )
    except TemplateValidationError as exc:
        status_code = 404 if str(exc) == "Template not found" else 400
        raise HTTPException(status_code=status_code, detail=str(exc)) from exc

    return dict(template)


@templates_router.post("/admin/templates/{template_id}/layout-preview")
def preview_template_layout(
    template_id: int,
    payload: TemplateLayoutPreviewRequest,
    _admin_user: dict[str, Any] = Depends(require_admin),
) -> Response:
    try:
        image_bytes = template_service.preview_template_layout(
            template_id=template_id,
            layout=payload.model_dump(
                include={
                    "top_text_x",
                    "top_text_y",
                    "top_text_width",
                    "bottom_text_x",
                    "bottom_text_y",
                    "bottom_text_width",
                }
            ),
            sample_text_top=payload.sample_text_top,
            sample_text_bottom=payload.sample_text_bottom,
            font_name=payload.font_name,
            font_size=payload.font_size,
            font_color=payload.font_color,
        )
    except TemplateValidationError as exc:
        status_code = 404 if str(exc) == "Template not found" else 400
        raise HTTPException(status_code=status_code, detail=str(exc)) from exc

    return Response(content=image_bytes, media_type="image/jpeg")
