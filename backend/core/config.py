from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[3]
PROJECT_ROOT = BASE_DIR
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "app.db"
GENERATED_IMAGES_DIR = DATA_DIR / "generated_images"
