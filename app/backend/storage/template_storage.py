import re
from io import BytesIO
from pathlib import Path
from uuid import uuid4

from PIL import Image, UnidentifiedImageError

from app.backend.core.config import TEMPLATES_DIR
from app.backend.storage.paths import build_relative_storage_path

ALLOWED_TEMPLATE_SUFFIXES = {".jpg", ".jpeg", ".png"}


def build_template_image_path(image_name: str) -> str:
    normalized = Path(image_name).name
    if not normalized:
        raise ValueError("Template image name required")
    if normalized != image_name:
        raise ValueError("Template image name must not contain directories")

    suffix = Path(normalized).suffix.lower()
    if suffix not in ALLOWED_TEMPLATE_SUFFIXES:
        raise ValueError("Incorrect file format")

    return build_relative_storage_path(TEMPLATES_DIR / normalized)


def store_uploaded_template_image(image_name: str, content: bytes) -> str:
    normalized = Path(image_name).name
    if not normalized:
        raise ValueError("Template image name required")
    if normalized != image_name:
        raise ValueError("Template image name must not contain directories")
    if not content:
        raise ValueError("Template image file is empty")

    suffix = Path(normalized).suffix.lower()
    if suffix not in ALLOWED_TEMPLATE_SUFFIXES:
        raise ValueError("Incorrect file format")

    try:
        with Image.open(BytesIO(content)) as image:
            image.verify()
    except (UnidentifiedImageError, OSError) as exc:
        raise ValueError("Incorrect file format") from exc

    safe_stem = re.sub(r"[^a-zA-Z0-9_-]+", "-", Path(normalized).stem).strip("-")
    if not safe_stem:
        safe_stem = "template"

    stored_name = f"{safe_stem}-{uuid4().hex[:8]}{suffix}"
    destination = TEMPLATES_DIR / stored_name
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(content)

    return build_relative_storage_path(destination)
