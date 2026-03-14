from pathlib import Path
from textwrap import wrap
from uuid import uuid4

from PIL import Image, ImageDraw, ImageFont, UnidentifiedImageError


class TemplateImageReadError(Exception):
    pass


def render_generated_image(
    template_path: Path,
    text_top: str,
    text_bottom: str,
    output_dir: Path,
) -> tuple[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        image = Image.open(template_path).convert("RGB")
    except UnidentifiedImageError as exc:
        raise TemplateImageReadError from exc

    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()

    _draw_text_block(draw, image, text_top, anchor="top", font=font)
    _draw_text_block(draw, image, text_bottom, anchor="bottom", font=font)

    share_token = uuid4().hex
    output_path = output_dir / f"{share_token}.jpg"
    image.save(output_path, format="JPEG")
    return share_token, output_path


def _draw_text_block(draw, image, text, anchor, font):
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
