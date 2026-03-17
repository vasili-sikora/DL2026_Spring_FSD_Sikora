from io import BytesIO
from pathlib import Path
from textwrap import wrap
from uuid import uuid4

from PIL import Image, ImageDraw, ImageFont, UnidentifiedImageError


class TemplateImageReadError(Exception):
    pass


class TemplateFontReadError(Exception):
    pass


SUPPORTED_FONTS = {
    "dejavu_sans": "DejaVuSans.ttf",
    "dejavu_serif": "NotoSerif-Regular.ttf",
    "dejavu_mono": "NotoSansMono-Regular.ttf",
}

FONTS_DIR = Path(__file__).resolve().parents[1] / "assets" / "fonts"


def render_generated_image(
    template_path: Path,
    text_top: str,
    text_bottom: str,
    font_name: str,
    font_size: int,
    output_dir: Path,
) -> tuple[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)

    image = _render_image(
        template_path=template_path,
        text_top=text_top,
        text_bottom=text_bottom,
        font_name=font_name,
        font_size=font_size,
    )

    share_token = uuid4().hex
    output_path = output_dir / f"{share_token}.jpg"
    image.save(output_path, format="JPEG")
    return share_token, output_path


def render_preview_image_bytes(
    template_path: Path,
    text_top: str,
    text_bottom: str,
    font_name: str,
    font_size: int,
) -> bytes:
    image = _render_image(
        template_path=template_path,
        text_top=text_top,
        text_bottom=text_bottom,
        font_name=font_name,
        font_size=font_size,
    )

    buffer = BytesIO()
    image.save(buffer, format="JPEG")
    return buffer.getvalue()


def _render_image(
    template_path: Path,
    text_top: str,
    text_bottom: str,
    font_name: str,
    font_size: int,
):
    try:
        image = Image.open(template_path).convert("RGB")
    except UnidentifiedImageError as exc:
        raise TemplateImageReadError from exc

    draw = ImageDraw.Draw(image)
    font = _load_font(font_name, font_size)

    _draw_text_block(draw, image, text_top, anchor="top", font=font)
    _draw_text_block(draw, image, text_bottom, anchor="bottom", font=font)

    return image


def _load_font(font_name: str, font_size: int):
    font_key = (font_name or "").strip().lower()
    font_file_name = SUPPORTED_FONTS.get(font_key)
    if not font_file_name:
        supported = ", ".join(sorted(SUPPORTED_FONTS))
        raise TemplateFontReadError(f"Unsupported font '{font_name}'. Use: {supported}")

    font_path = FONTS_DIR / font_file_name

    try:
        return ImageFont.truetype(font_path, size=font_size)
    except OSError as exc:
        raise TemplateFontReadError(
            f"Cannot load font '{font_name}' from assets/fonts"
        ) from exc


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
