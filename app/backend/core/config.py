import os
from pathlib import Path
from typing import Final, Literal, cast

BASE_DIR: Final[Path] = Path(__file__).resolve().parents[3]


def _load_env_file(env_path: Path) -> None:
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'").strip('"')
        os.environ.setdefault(key, value)


def _get_bool_env(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _get_int_env(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    return int(value)


def _get_path_env(name: str, default: Path) -> Path:
    value = os.getenv(name)
    if not value:
        return default

    candidate = Path(value)
    if candidate.is_absolute():
        return candidate
    return BASE_DIR / candidate


def _get_list_env(name: str) -> list[str]:
    value = os.getenv(name, "")
    return [item.strip() for item in value.split(",") if item.strip()]


_load_env_file(BASE_DIR / ".env")

DATA_DIR: Final[Path] = _get_path_env("DATA_DIR", BASE_DIR / "data")
DB_PATH: Final[Path] = _get_path_env("DB_PATH", DATA_DIR / "app.db")
GENERATED_IMAGES_DIR: Final[Path] = _get_path_env(
    "GENERATED_IMAGES_DIR", DATA_DIR / "generated_images"
)
TEMPLATES_DIR: Final[Path] = _get_path_env("TEMPLATES_DIR", DATA_DIR / "templates")

APP_DIR: Final[Path] = BASE_DIR / "app"
FRONTEND_DIR: Final[Path] = APP_DIR / "frontend"

SESSION_SECRET_KEY: Final[str] = os.getenv(
    "SESSION_SECRET_KEY", "change-me-local-dev-only"
)
SESSION_COOKIE_NAME: Final[str] = os.getenv("SESSION_COOKIE_NAME", "devcraft_session")
SessionSameSite = Literal["lax", "strict", "none"]


def _get_samesite_env(name: str, default: SessionSameSite) -> SessionSameSite:
    value = os.getenv(name)
    if value is None:
        return default

    normalized = value.strip().lower()
    if normalized not in {"lax", "strict", "none"}:
        return default
    return cast(SessionSameSite, normalized)


SESSION_COOKIE_SAMESITE: Final[SessionSameSite] = _get_samesite_env(
    "SESSION_COOKIE_SAMESITE", "lax"
)
SESSION_COOKIE_SECURE: Final[bool] = _get_bool_env("SESSION_COOKIE_SECURE", False)
SESSION_MAX_AGE_SECONDS: Final[int] = _get_int_env(
    "SESSION_MAX_AGE_SECONDS", 60 * 60 * 24 * 7
)

SQLALCHEMY_DATABASE_URL: Final[str] = f"sqlite:///{DB_PATH}"
CORS_ALLOWED_ORIGINS: Final[list[str]] = _get_list_env("CORS_ALLOWED_ORIGINS")
SQLITE_BUSY_TIMEOUT_MS: Final[int] = _get_int_env("SQLITE_BUSY_TIMEOUT_MS", 5000)
SQLITE_ENABLE_WAL: Final[bool] = _get_bool_env("SQLITE_ENABLE_WAL", True)
SQLITE_SYNCHRONOUS: Final[str] = os.getenv("SQLITE_SYNCHRONOUS", "NORMAL").upper()
