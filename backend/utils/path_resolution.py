from pathlib import Path

from app.backend.core.config import BASE_DIR


def resolve_storage_path(path_value: str | Path) -> Path:
    candidate = Path(path_value)
    if candidate.is_absolute():
        return candidate

    base_candidate = BASE_DIR / candidate
    if base_candidate.exists():
        return base_candidate

    return base_candidate
