from pathlib import Path
from typing import Any

from app.backend.core.config import BASE_DIR, GENERATED_IMAGES_DIR
from app.backend.models.generated_images import GenerateImageRequest
from app.backend.repositories.generated_images_repo import (
    GeneratedImagesRepository,
)
from app.backend.repositories.templates_repo import TemplateRepository
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
    render_preview_image_bytes,
)
from app.backend.utils.path_resolution import resolve_storage_path

RowMapping = dict[str, Any]


class GeneratedImagesService:
    def __init__(
        self,
        generated_images_repo: GeneratedImagesRepository,
        templates_repo: TemplateRepository,
    ) -> None:
        self.generated_images_repo = generated_images_repo
        self.templates_repo = templates_repo

    def get_all_images(self, user_id: int) -> list[RowMapping]:
        if user_id < 1:
            raise ValueError("Invalid user id")
        images = self.generated_images_repo.get_all_images(user_id)

        return [dict(image) for image in images]

    def get_image_by_id(self, image_id: int, user_id: int) -> RowMapping:
        image = self.generated_images_repo.get_image_by_id(image_id, user_id)
        if not image:
            raise ImageNotFoundError("Image not found")
        return dict(image)

    def generate_image(
        self, template_id: int, payload: GenerateImageRequest
    ) -> RowMapping:
        template_path = self._get_template_image_path(template_id)

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
        if not record:
            raise ValueError("Failed to create generated image")
        return dict(record)

    def preview_image(self, template_id: int, payload: GenerateImageRequest) -> bytes:
        if payload.font_size < 12 or payload.font_size > 120:
            raise ValueError("Invalid font size")
        template_path = self._get_template_image_path(template_id)

        try:
            return render_preview_image_bytes(
                template_path=template_path,
                text_top=payload.text_top,
                text_bottom=payload.text_bottom,
                font_name=payload.font_name,
                font_size=payload.font_size,
            )
        except TemplateImageReadError as exc:
            raise TemplateImageFormatError(
                "Template image format is not supported. Use JPEG or PNG."
            ) from exc
        except TemplateFontReadError as exc:
            raise TemplateFontError(str(exc)) from exc

    def _get_template_image_path(self, template_id: int) -> Path:
        template = self.templates_repo.get_template_by_id(template_id)
        if not template:
            raise TemplateNotFoundError("Template not found")

        template_path = resolve_storage_path(template["image_path"])
        if not template_path.exists():
            raise TemplateImageFileNotFoundError("Template image file not found")
        return template_path

    def get_image_by_share_token(self, share_token: str) -> RowMapping:
        image = self.generated_images_repo.get_image_by_share_token(share_token)

        if not image:
            raise ImageNotFoundError("Image not found")

        return dict(image)
