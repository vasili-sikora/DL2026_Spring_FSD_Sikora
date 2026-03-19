import string
from pathlib import Path

import pytest
from PIL import Image

from app.backend.utils.image_generation import (
    TemplateFontReadError,
    TemplateImageReadError,
    render_generated_image,
    render_preview_image_bytes,
)


def test_render_preview_image_bytes_returns_jpeg_for_unicode_text(
    tmp_path: Path,
) -> None:
    template_path = tmp_path / "template.jpg"
    Image.new("RGB", (640, 480), color=(20, 30, 40)).save(template_path, format="JPEG")

    result = render_preview_image_bytes(
        template_path=template_path,
        text_top="😀 Верхний текст",
        text_bottom="Нижний текст 😺",
        font_name="dejavu_sans",
        font_size=36,
    )

    assert result.startswith(b"\xff\xd8")
    assert len(result) > 100


def test_render_generated_image_creates_file_and_token(tmp_path: Path) -> None:
    template_path = tmp_path / "template.png"
    output_dir = tmp_path / "generated"
    Image.new("RGB", (500, 500), color=(255, 255, 255)).save(
        template_path, format="PNG"
    )

    token, output_path = render_generated_image(
        template_path=template_path,
        text_top="TOP",
        text_bottom="BOTTOM",
        font_name="dejavu_mono",
        font_size=32,
        output_dir=output_dir,
    )

    assert len(token) == 32
    assert all(ch in string.hexdigits for ch in token)
    assert output_path.exists()
    assert output_path.suffix == ".jpg"
    assert output_path.read_bytes().startswith(b"\xff\xd8")


def test_render_preview_raises_on_unsupported_font(tmp_path: Path) -> None:
    template_path = tmp_path / "template.jpg"
    Image.new("RGB", (300, 300), color=(10, 10, 10)).save(template_path, format="JPEG")

    with pytest.raises(TemplateFontReadError, match="Unsupported font"):
        render_preview_image_bytes(
            template_path=template_path,
            text_top="text",
            text_bottom="text",
            font_name="totally_unknown_font",
            font_size=30,
        )


def test_render_preview_raises_on_invalid_template_file(tmp_path: Path) -> None:
    template_path = tmp_path / "not_image.jpg"
    template_path.write_text("not an image", encoding="utf-8")

    with pytest.raises(TemplateImageReadError):
        render_preview_image_bytes(
            template_path=template_path,
            text_top="text",
            text_bottom="text",
            font_name="dejavu_sans",
            font_size=30,
        )
