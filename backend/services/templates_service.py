from app.backend.repositories.templates.templates_repo import TemplateRepository


class TemplateService:
    def __init__(self, repo: TemplateRepository):
        self.repo = repo

    def create_template(self, template):
        if not template["name"]:
            raise ValueError("Template name required")

        return self.repo.create_template(template)

    def get_all_templates(self):
        return self.repo.get_all_templates()
