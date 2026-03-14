from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.backend.api.generated_images_routes import generated_images_router
from app.backend.api.templates_routes import templates_router

app = FastAPI()

app.include_router(templates_router)
app.include_router(generated_images_router)

FRONTEND_DIR = Path(__file__).resolve().parents[1] / "frontend"


@app.get("/")
def root():
    return FileResponse(FRONTEND_DIR / "index.html")


app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")
