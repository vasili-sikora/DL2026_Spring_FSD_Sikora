from pathlib import Path
from typing import Any, Mapping, Protocol

from PIL import Image

from app.backend.services.exceptions import TemplateValidationError
from app.backend.storage.paths import resolve_storage_path
from app.backend.storage.template_storage import (
    build_template_image_path,
    store_uploaded_template_image,
)
from app.backend.utils.image_generation import (
    TemplateFontReadError,
    TemplateImageReadError,
    render_preview_image_bytes,
)

TemplatePayload = Mapping[str, Any]
TemplateRow = dict[str, Any]


class TemplateRepoLike(Protocol):
    def create_template(self, template: dict[str, Any]) -> Any: ...
    def get_all_templates(self) -> list[Any]: ...
    def get_template_by_id(self, template_id: int) -> Any: ...
    def update_template_layout(
        self, template_id: int, layout: dict[str, int]
    ) -> Any: ...


class TemplateService:
    def __init__(self, repo: TemplateRepoLike) -> None:
        self.repo = repo

    def create_template(self, template: TemplatePayload) -> TemplateRow:
        if not template["name"]:
            raise TemplateValidationError("Template name required")

        try:
            image_path = build_template_image_path(template["image_name"])
        except ValueError as exc:
            raise TemplateValidationError(str(exc)) from exc

        created = self.repo.create_template(
            {
                "name": template["name"],
                "image_path": image_path,
            }
        )
        if not created:
            raise TemplateValidationError("Failed to create template")
        return dict(created)

    def get_all_templates(self) -> list[TemplateRow]:
        rows = self.repo.get_all_templates()
        return [self._with_layout_defaults(dict(row)) for row in rows]

    def get_template_by_id(self, template_id: int) -> TemplateRow | None:
        row = self.repo.get_template_by_id(template_id)
        if not row:
            return None
        return self._with_layout_defaults(dict(row))

    def create_template_from_upload(
        self,
        name: str,
        image_name: str,
        image_content: bytes,
    ) -> TemplateRow:
        if not name:
            raise TemplateValidationError("Template name required")

        try:
            image_path = store_uploaded_template_image(image_name, image_content)
        except ValueError as exc:
            raise TemplateValidationError(str(exc)) from exc

        try:
            created = self.repo.create_template(
                {
                    "name": name,
                    "image_path": image_path,
                    **self._build_default_layout(resolve_storage_path(image_path)),
                }
            )
        except Exception:
            resolve_storage_path(image_path).unlink(missing_ok=True)
            raise

        if not created:
            resolve_storage_path(image_path).unlink(missing_ok=True)
            raise TemplateValidationError("Failed to create template")

        return dict(created)

    def update_template_layout(
        self, template_id: int, layout: Mapping[str, int]
    ) -> TemplateRow:
        template = self.get_template_by_id(template_id)
        if not template:
            raise TemplateValidationError("Template not found")

        template_path = resolve_storage_path(template["image_path"])
        if not template_path.exists():
            raise TemplateValidationError("Template image file not found")

        self._validate_layout(template_path, layout)

        updated = self.repo.update_template_layout(template_id, dict(layout))
        if not updated:
            raise TemplateValidationError("Failed to update template layout")

        return dict(updated)

    def preview_template_layout(
        self,
        template_id: int,
        layout: Mapping[str, int],
        sample_text_top: str,
        sample_text_bottom: str,
        font_name: str,
        font_size: int,
        font_color: str,
    ) -> bytes:
        template = self.get_template_by_id(template_id)
        if not template:
            raise TemplateValidationError("Template not found")

        template_path = resolve_storage_path(template["image_path"])
        if not template_path.exists():
            raise TemplateValidationError("Template image file not found")

        self._validate_layout(template_path, layout)

        try:
            return render_preview_image_bytes(
                template_path=template_path,
                text_top=sample_text_top,
                text_bottom=sample_text_bottom,
                font_name=font_name,
                font_size=font_size,
                font_color=font_color,
                template_layout=dict(layout),
            )
        except TemplateImageReadError as exc:
            raise TemplateValidationError(
                "Template image format is not supported"
            ) from exc
        except TemplateFontReadError as exc:
            raise TemplateValidationError(str(exc)) from exc

    def _build_default_layout(self, image_path: Path) -> dict[str, int]:
        with Image.open(image_path) as image:
            width = image.width
            height = image.height

        horizontal_margin = max(20, width // 16)
        text_width = max(80, width - horizontal_margin * 2)
        top_y = max(20, height // 24)
        bottom_y = max(top_y + 40, height - max(80, height // 5))

        return {
            "top_text_x": horizontal_margin,
            "top_text_y": top_y,
            "top_text_width": text_width,
            "bottom_text_x": horizontal_margin,
            "bottom_text_y": bottom_y,
            "bottom_text_width": text_width,
        }

    def _validate_layout(self, template_path: Path, layout: Mapping[str, int]) -> None:
        with Image.open(template_path) as image:
            width = image.width
            height = image.height

        for prefix in ("top", "bottom"):
            x = int(layout[f"{prefix}_text_x"])
            y = int(layout[f"{prefix}_text_y"])
            block_width = int(layout[f"{prefix}_text_width"])

            if x >= width:
                raise TemplateValidationError(
                    f"{prefix.title()} text x is outside image"
                )
            if y >= height:
                raise TemplateValidationError(
                    f"{prefix.title()} text y is outside image"
                )
            if x + block_width > width:
                raise TemplateValidationError(
                    f"{prefix.title()} text block exceeds image width"
                )

    def _with_layout_defaults(self, template: TemplateRow) -> TemplateRow:
        if all(
            template.get(key) is not None
            for key in (
                "top_text_x",
                "top_text_y",
                "top_text_width",
                "bottom_text_x",
                "bottom_text_y",
                "bottom_text_width",
            )
        ):
            return template

        template_path = resolve_storage_path(template["image_path"])
        if not template_path.exists():
            return template

        defaults = self._build_default_layout(template_path)
        for key, value in defaults.items():
            if template.get(key) is None:
                template[key] = value
        return template
