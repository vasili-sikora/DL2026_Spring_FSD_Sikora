from app.backend.core.config import BASE_DIR, GENERATED_IMAGES_DIR
from app.backend.repositories.generated_images.generated_images_repo import (
    GeneratedImagesRepository,
)
from app.backend.repositories.templates.templates_repo import TemplateRepository
from app.backend.services.exceptions import (
    ImageNotFoundError,
    TemplateFontError,
    TemplateImageFileNotFoundError,
    TemplateImageFormatError,
    TemplateNotFoundError,
)
from app.backend.utils.image_generation import (
    TemplateFontReadError,
    TemplateImageReadError,
    render_generated_image,
)
from app.backend.utils.path_resolution import resolve_storage_path


class GeneratedImagesService:
    def __init__(
        self,
        generated_images_repo: GeneratedImagesRepository,
        templates_repo: TemplateRepository,
    ):
        self.generated_images_repo = generated_images_repo
        self.templates_repo = templates_repo

    def get_all_images(self):
        images = self.generated_images_repo.get_all_images()
        if not images:
            raise ImageNotFoundError("Images not found")
        return images

    def get_image_by_id(self, image_id: int):
        image = self.generated_images_repo.get_image_by_id(image_id)
        if not image:
            raise ImageNotFoundError("Image not found")
        return image

    def generate_image(self, template_id: int, payload):
        template = self.templates_repo.get_template_by_id(template_id)
        if not template:
            raise TemplateNotFoundError("Template not found")

        template_path = resolve_storage_path(template["image_path"])
        if not template_path.exists():
            raise TemplateImageFileNotFoundError("Template image file not found")

        try:
            share_token, output_path = render_generated_image(
                template_path=template_path,
                text_top=payload.text_top,
                text_bottom=payload.text_bottom,
                font_name=payload.font_name,
                font_size=payload.font_size,
                output_dir=GENERATED_IMAGES_DIR,
            )
        except TemplateImageReadError as exc:
            raise TemplateImageFormatError(
                "Template image format is not supported. Use JPEG or PNG."
            ) from exc
        except TemplateFontReadError as exc:
            raise TemplateFontError(str(exc)) from exc

        record = self.generated_images_repo.create_image(
            {
                "template_id": template_id,
                "text_top": payload.text_top,
                "text_bottom": payload.text_bottom,
                "image_path": str(output_path.relative_to(BASE_DIR)),
                "share_token": share_token,
            }
        )
        return record

    def get_image_by_share_token(self, share_token: str):
        image = self.generated_images_repo.get_image_by_share_token(share_token)

        if not image:
            raise ImageNotFoundError("Image not found")

        return image
