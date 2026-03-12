from pathlib import Path
from textwrap import wrap
from uuid import uuid4

from fastapi import HTTPException
from PIL import Image, ImageDraw, ImageFont, UnidentifiedImageError

from app.backend.core.config import BASE_DIR, GENERATED_IMAGES_DIR, PROJECT_ROOT
from app.backend.repositories.generated_images.generated_images_repo import (
    GeneratedImagesRepository,
)
from app.backend.repositories.templates.templates_repo import TemplateRepository


class GeneratedImagesService:
    def __init__(
        self,
        generated_images_repo: GeneratedImagesRepository,
        templates_repo: TemplateRepository,
    ):
        self.generated_images_repo = generated_images_repo
        self.templates_repo = templates_repo

    def get_all_images(self):
        return self.generated_images_repo.get_all_images()

    def get_image_by_id(self, image_id: int):
        return self.generated_images_repo.get_image_by_id(image_id)

    def generate_image(self, template_id: int, payload):
        template = self.templates_repo.get_template_by_id(template_id)
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")

        template_path = self._resolve_template_path(template["image_path"])
        if not template_path.exists():
            raise HTTPException(status_code=404, detail="Template image file not found")

        GENERATED_IMAGES_DIR.mkdir(parents=True, exist_ok=True)

        try:
            image = Image.open(template_path).convert("RGB")
        except UnidentifiedImageError as exc:
            raise HTTPException(
                status_code=400,
                detail="Template image format is not supported. Use JPEG or PNG.",
            ) from exc

        draw = ImageDraw.Draw(image)
        font = ImageFont.load_default()

        self._draw_text_block(draw, image, payload.text_top, anchor="top", font=font)
        self._draw_text_block(
            draw, image, payload.text_bottom, anchor="bottom", font=font
        )

        share_token = uuid4().hex
        output_name = f"{share_token}.jpg"
        output_path = GENERATED_IMAGES_DIR / output_name
        image.save(output_path, format="JPEG")

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

    def _resolve_template_path(self, image_path):
        candidate = Path(image_path)
        if candidate.is_absolute():
            return candidate

        base_candidate = BASE_DIR / candidate
        if base_candidate.exists():
            return base_candidate

        project_candidate = PROJECT_ROOT / candidate
        if project_candidate.exists():
            return project_candidate

        return base_candidate

    def _draw_text_block(self, draw, image, text, anchor, font):
        content = (text or "").strip()
        if not content:
            return

        wrapped = "\n".join(wrap(content, width=24)) or content
        bbox = draw.multiline_textbbox((0, 0), wrapped, font=font, stroke_width=2)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (image.width - text_width) / 2
        y = 20 if anchor == "top" else image.height - text_height - 20

        draw.multiline_text(
            (x, y),
            wrapped,
            font=font,
            fill="white",
            stroke_width=2,
            stroke_fill="black",
            align="center",
        )

    def get_image_by_share_token(self, share_token: str):
        image = self.generated_images_repo.get_image_by_share_token(share_token)

        if not image:
            raise HTTPException(status_code=404, detail="Image not found")

        return image
