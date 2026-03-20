from pathlib import Path

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
