from pathlib import Path
from typing import Final

BASE_DIR: Final[Path] = Path(__file__).resolve().parents[3]
DATA_DIR: Final[Path] = BASE_DIR / "data"
DB_PATH: Final[Path] = DATA_DIR / "app.db"
GENERATED_IMAGES_DIR: Final[Path] = DATA_DIR / "generated_images"
TEMPLATES_DIR: Final[Path] = DATA_DIR / "templates"

APP_DIR: Final[Path] = BASE_DIR / "app"
FRONTEND_DIR: Final[Path] = APP_DIR / "frontend"
