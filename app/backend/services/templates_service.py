from typing import Any, Mapping

from app.backend.repositories.templates_repo import TemplateRepository
from app.backend.storage.template_storage import build_template_image_path

TemplatePayload = Mapping[str, str]
TemplateRow = dict[str, Any]


class TemplateService:
    def __init__(self, repo: TemplateRepository) -> None:
        self.repo = repo

    def create_template(self, template: TemplatePayload) -> TemplateRow:
        if not template["name"]:
            raise ValueError("Template name required")

        image_path = build_template_image_path(template["image_name"])

        created = self.repo.create_template(
            {
                "name": template["name"],
                "image_path": image_path,
            }
        )
        if not created:
            raise ValueError("Failed to create template")
        return dict(created)

    def get_all_templates(self) -> list[TemplateRow]:
        rows = self.repo.get_all_templates()
        return [dict(row) for row in rows]

    def get_template_by_id(self, template_id: int) -> TemplateRow | None:
        row = self.repo.get_template_by_id(template_id)
        if not row:
            return None
        return dict(row)
