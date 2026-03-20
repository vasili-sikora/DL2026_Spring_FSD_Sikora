from pathlib import Path

from app.backend.core.config import BASE_DIR


def resolve_storage_path(path_value: str | Path) -> Path:
    candidate = Path(path_value)
    if candidate.is_absolute():
        if candidate.exists():
            return candidate

        try:
            data_index = candidate.parts.index("data")
        except ValueError:
            return candidate

        return BASE_DIR / Path(*candidate.parts[data_index:])

    return BASE_DIR / candidate


def build_relative_storage_path(path_value: Path) -> str:
    try:
        return str(path_value.relative_to(BASE_DIR))
    except ValueError as exc:
        raise ValueError(
            "Storage path must stay inside project base directory"
        ) from exc
