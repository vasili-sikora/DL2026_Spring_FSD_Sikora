from pathlib import Path

from app.backend.core.config import BASE_DIR


def resolve_storage_path(path_value: str | Path) -> Path:
    candidate = Path(path_value)
    if candidate.is_absolute():
        if candidate.exists():
            return candidate

        # Support old absolute paths persisted before project directory move.
        try:
            data_index = candidate.parts.index("data")
        except ValueError:
            return candidate

        migrated = BASE_DIR / Path(*candidate.parts[data_index:])
        return migrated

    base_candidate = BASE_DIR / candidate
    if base_candidate.exists():
        return base_candidate

    return base_candidate
