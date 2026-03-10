from fastapi import APIRouter

from app.backend.db.sqlite_conn import SQLiteConnection
from app.backend.repositories.templates.templates_repo import TemplateRepository
from app.backend.services.templates_service import TemplateService

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
