from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from starlette.responses import FileResponse

from app.backend.auth.dependencies import require_admin
from app.backend.dependencies import template_service
from app.backend.models.templates import TemplateCreate
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
