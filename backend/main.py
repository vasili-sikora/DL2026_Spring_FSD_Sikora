from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.backend.api.generated_images_routes import generated_images_router
from app.backend.api.templates_routes import templates_router
from app.backend.core.rate_limit import limiter

app = FastAPI()

app.include_router(templates_router)
app.include_router(generated_images_router)

# пока что просто пусть будут, скорее всего жирно
app.add_middleware(CORSMiddleware)
app.add_middleware(GZipMiddleware, minimum_size=1000, compresslevel=5)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)
FRONTEND_DIR = Path(__file__).resolve().parents[1] / "frontend"


@app.get("/")
def root():
    return FileResponse(FRONTEND_DIR / "index.html")


app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")
