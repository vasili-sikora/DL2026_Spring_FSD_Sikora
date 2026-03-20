from typing import Any, Protocol

from app.backend.core.config import GENERATED_IMAGES_DIR
from app.backend.models.generated_images import (
    GenerateImageRequest,
    PreviewImageRequest,
)
from app.backend.services.exceptions import (
    ImageGenerationValidationError,
    ImageNotFoundError,
    ImagePersistenceError,
    InvalidUserContextError,
    TemplateFontError,
    TemplateImageFileNotFoundError,
    TemplateImageFormatError,
    TemplateNotFoundError,
)
from app.backend.storage.paths import build_relative_storage_path, resolve_storage_path
from app.backend.utils.image_generation import (
    TemplateFontReadError,
    TemplateImageReadError,
    render_generated_image,
    render_preview_image_bytes,
)

RowMapping = dict[str, Any]


class GeneratedImagesRepoLike(Protocol):
    def get_all_images(self, user_id: int) -> list[Any]: ...
    def get_image_by_id(self, image_id: int, user_id: int) -> Any: ...
    def create_image(self, image: dict[str, Any]) -> Any: ...
    def get_image_by_share_token(self, share_token: str) -> Any: ...


class TemplateRepoLike(Protocol):
    def get_template_by_id(self, template_id: int) -> Any: ...


class GeneratedImagesService:
    def __init__(
        self,
        generated_images_repo: GeneratedImagesRepoLike,
        templates_repo: TemplateRepoLike,
    ) -> None:
        self.generated_images_repo = generated_images_repo
        self.templates_repo = templates_repo

    def get_all_images(self, user_id: int) -> list[RowMapping]:
        if user_id < 1:
            raise InvalidUserContextError("Invalid user id")
        images = self.generated_images_repo.get_all_images(user_id)

        return [dict(image) for image in images]

    def get_image_by_id(self, image_id: int, user_id: int) -> RowMapping:
        image = self.generated_images_repo.get_image_by_id(image_id, user_id)
        if not image:
            raise ImageNotFoundError("Image not found")
        return dict(image)

    def generate_image(
        self, template_id: int, payload: GenerateImageRequest, user_id: int
    ) -> RowMapping:
        template = self._get_template(template_id)
        template_path = resolve_storage_path(template["image_path"])

        try:
            share_token, output_path = render_generated_image(
                template_path=template_path,
                text_top=payload.text_top,
                text_bottom=payload.text_bottom,
                font_name=payload.font_name,
                font_size=payload.font_size,
                font_color=payload.font_color,
                template_layout=template,
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
                "image_path": build_relative_storage_path(output_path),
                "share_token": share_token,
                "user_id": user_id,
            }
        )
        if not record:
            raise ImagePersistenceError("Failed to create generated image")
        return dict(record)

    def preview_image(self, template_id: int, payload: PreviewImageRequest) -> bytes:
        if payload.font_size < 12 or payload.font_size > 120:
            raise ImageGenerationValidationError("Invalid font size")
        template = self._get_template(template_id)
        template_path = resolve_storage_path(template["image_path"])

        try:
            return render_preview_image_bytes(
                template_path=template_path,
                text_top=payload.text_top,
                text_bottom=payload.text_bottom,
                font_name=payload.font_name,
                font_size=payload.font_size,
                font_color=payload.font_color,
                template_layout=template,
            )
        except TemplateImageReadError as exc:
            raise TemplateImageFormatError(
                "Template image format is not supported. Use JPEG or PNG."
            ) from exc
        except TemplateFontReadError as exc:
            raise TemplateFontError(str(exc)) from exc

    def _get_template(self, template_id: int) -> RowMapping:
        template = self.templates_repo.get_template_by_id(template_id)
        if not template:
            raise TemplateNotFoundError("Template not found")

        template_path = resolve_storage_path(template["image_path"])
        if not template_path.exists():
            raise TemplateImageFileNotFoundError("Template image file not found")
        return dict(template)

    def get_image_by_share_token(self, share_token: str) -> RowMapping:
        image = self.generated_images_repo.get_image_by_share_token(share_token)

        if not image:
            raise ImageNotFoundError("Image not found")

        return dict(image)
