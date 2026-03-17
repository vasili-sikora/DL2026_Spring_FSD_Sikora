from app.backend.repositories.templates_repo import TemplateRepository


class TemplateService:
    def __init__(self, repo: TemplateRepository):
        self.repo = repo

    def create_template(self, template):
        if not template["name"]:
            raise ValueError("Template name required")
        if not template["image_name"].endswith((".jpeg", ".png", "jpg")):
            raise ValueError("Incorrect file format")

        return self.repo.create_template(template)

    def get_all_templates(self):
        return self.repo.get_all_templates()

    def get_template_by_id(self, template_id: int):
        return self.repo.get_template_by_id(template_id)
