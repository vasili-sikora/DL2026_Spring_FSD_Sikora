from fastapi import FastAPI

from app.backend.api.templates_routes import templates_router
from app.backend.api.generated_images_routes import generated_images_router

app = FastAPI()

app.include_router(templates_router)
app.include_router(generated_images_router)