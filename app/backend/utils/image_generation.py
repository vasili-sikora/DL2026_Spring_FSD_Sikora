from io import BytesIO
from pathlib import Path
from typing import Any, Final
from uuid import uuid4

from PIL import Image, ImageDraw, ImageFont, UnidentifiedImageError


class TemplateImageReadError(Exception):
    pass


class TemplateFontReadError(Exception):
    pass


SUPPORTED_FONTS: Final[dict[str, str]] = {
    "dejavu_sans": "DejaVuSans.ttf",
    "dejavu_serif": "NotoSerif-Regular.ttf",
    "dejavu_mono": "NotoSansMono-Regular.ttf",
}

FONTS_DIR: Final[Path] = Path(__file__).resolve().parents[1] / "assets" / "fonts"


def render_generated_image(
    template_path: Path,
    text_top: str,
    text_bottom: str,
    font_name: str,
    font_size: int,
    font_color: str,
    output_dir: Path,
    template_layout: dict[str, Any] | None = None,
) -> tuple[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)

    image = _render_image(
        template_path=template_path,
        text_top=text_top,
        text_bottom=text_bottom,
        font_name=font_name,
        font_size=font_size,
        font_color=font_color,
        template_layout=template_layout,
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
    font_color: str,
    template_layout: dict[str, Any] | None = None,
) -> bytes:
    image = _render_image(
        template_path=template_path,
        text_top=text_top,
        text_bottom=text_bottom,
        font_name=font_name,
        font_size=font_size,
        font_color=font_color,
        template_layout=template_layout,
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
    font_color: str,
    template_layout: dict[str, Any] | None,
) -> Image.Image:
    try:
        image = Image.open(template_path).convert("RGB")
    except UnidentifiedImageError as exc:
        raise TemplateImageReadError from exc

    draw = ImageDraw.Draw(image)
    font = _load_font(font_name, font_size)
    resolved_layout = _resolve_template_layout(image, template_layout)

    _draw_text_block(
        draw,
        text_top,
        font=font,
        font_color=font_color,
        box=resolved_layout["top"],
    )
    _draw_text_block(
        draw,
        text_bottom,
        font=font,
        font_color=font_color,
        box=resolved_layout["bottom"],
    )

    return image


def _load_font(font_name: str, font_size: int) -> ImageFont.FreeTypeFont:
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


def _draw_text_block(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.FreeTypeFont,
    font_color: str,
    box: dict[str, int],
) -> None:
    content = (text or "").strip()
    if not content:
        return

    wrapped = _wrap_text_to_width(draw, content, font, box["width"]) or content
    bbox = draw.multiline_textbbox((0, 0), wrapped, font=font, stroke_width=2)
    text_width = bbox[2] - bbox[0]
    x = box["x"] + max(0, (box["width"] - text_width) / 2)
    y = box["y"]

    draw.multiline_text(
        (x, y),
        wrapped,
        font=font,
        fill=font_color,
        stroke_width=2,
        stroke_fill="black",
        align="center",
    )


def _resolve_template_layout(
    image: Image.Image, template_layout: dict[str, Any] | None
) -> dict[str, dict[str, int]]:
    horizontal_margin = max(20, image.width // 16)
    default_width = max(80, image.width - horizontal_margin * 2)
    default_top_y = max(20, image.height // 24)
    default_bottom_y = max(
        default_top_y + 40, image.height - max(80, image.height // 5)
    )

    layout = template_layout or {}

    def pick_int(key: str, fallback: int) -> int:
        value = layout.get(key)
        return fallback if value is None else int(value)

    return {
        "top": {
            "x": pick_int("top_text_x", horizontal_margin),
            "y": pick_int("top_text_y", default_top_y),
            "width": pick_int("top_text_width", default_width),
        },
        "bottom": {
            "x": pick_int("bottom_text_x", horizontal_margin),
            "y": pick_int("bottom_text_y", default_bottom_y),
            "width": pick_int("bottom_text_width", default_width),
        },
    }


def _wrap_text_to_width(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.FreeTypeFont,
    max_width: int,
) -> str:
    lines: list[str] = []
    for paragraph in text.splitlines() or [text]:
        words = paragraph.split()
        if not words:
            lines.append("")
            continue

        current = words[0]
        for word in words[1:]:
            candidate = f"{current} {word}"
            bbox = draw.textbbox((0, 0), candidate, font=font, stroke_width=2)
            candidate_width = bbox[2] - bbox[0]
            if candidate_width <= max_width:
                current = candidate
            else:
                lines.append(current)
                current = word
        lines.append(current)

    return "\n".join(lines)
