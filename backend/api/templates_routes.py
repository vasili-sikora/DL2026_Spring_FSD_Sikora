from fastapi import APIRouter, HTTPException
from starlette.responses import FileResponse

from app.backend.db.sqlite_conn import SQLiteConnection
from app.backend.models.templates import TemplateCreate
from app.backend.repositories.templates.templates_repo import TemplateRepository
from app.backend.services.templates_service import TemplateService
from app.backend.utils.path_resolution import resolve_storage_path

templates_router = APIRouter()

db = SQLiteConnection()
template_repo = TemplateRepository(db)
template_service = TemplateService(template_repo)


@templates_router.get("/templates")
def get_templates():
    templates = template_service.get_all_templates()

    return [dict(template) for template in templates]


@templates_router.get("/templates/{template_id}")
def get_template_by_id(template_id: int):
    template = template_service.get_template_by_id(template_id)

    return dict(template) if template else None


@templates_router.get("/templates/{template_id}/image")
def get_template_image(template_id: int):
    template = template_service.get_template_by_id(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    resolved_path = resolve_storage_path(template["image_path"])

    if not resolved_path.exists():
        raise HTTPException(status_code=404, detail="Template image file not found")

    return FileResponse(resolved_path)


@templates_router.post("/templates")
def create_template(payload: TemplateCreate):
    template = template_service.create_template(payload.model_dump())
    return dict(template)
