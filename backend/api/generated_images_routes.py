from fastapi import APIRouter, HTTPException
from starlette.responses import FileResponse

from app.backend.core.config import PROJECT_ROOT
from app.backend.db.sqlite_conn import SQLiteConnection
from app.backend.models.generated_images import (
    ErrorResponse,
    GeneratedImageResponse,
    GenerateImageRequest,
)
from app.backend.repositories.generated_images.generated_images_repo import (
    GeneratedImagesRepository,
)
from app.backend.repositories.templates.templates_repo import TemplateRepository
from app.backend.services.exceptions import (
    ImageNotFoundError,
    TemplateImageFileNotFoundError,
    TemplateImageFormatError,
    TemplateNotFoundError,
)
from app.backend.services.generated_images_service import GeneratedImagesService

generated_images_router = APIRouter()

db = SQLiteConnection()
generated_images_repo = GeneratedImagesRepository(db)
templates_repo = TemplateRepository(db)
generated_images_service = GeneratedImagesService(generated_images_repo, templates_repo)


@generated_images_router.get("/generated_images")
def get_images():
    try:
        images = generated_images_service.get_all_images()
    except ImageNotFoundError as e:
        raise HTTPException(status_code=404, detail="Images not found")

    return [dict(image) for image in images]


@generated_images_router.get(
    "/generated_images/{image_id}",
    response_model=GeneratedImageResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Image not found"},
    },
)
def get_image_by_id(image_id: int):
    try:
        image = generated_images_service.get_image_by_id(image_id)
    except ImageNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return GeneratedImageResponse(**dict(image))


@generated_images_router.post(
    "/templates/{template_id}/generate",
    response_model=GeneratedImageResponse,
    responses={
        400: {
            "model": ErrorResponse,
            "description": "Template image format is not supported",
        },
        404: {
            "model": ErrorResponse,
            "description": "Template or template image file not found",
        },
    },
)
def generate_image(template_id: int, payload: GenerateImageRequest):
    try:
        image = generated_images_service.generate_image(template_id, payload)
    except TemplateNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except TemplateImageFileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except TemplateImageFormatError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return GeneratedImageResponse(**dict(image))


@generated_images_router.get("/images/{share_token}")
def get_image_by_share_token(share_token: str):
    try:
        image = generated_images_service.get_image_by_share_token(share_token)
    except ImageNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    path = PROJECT_ROOT / image["image_path"]

    return FileResponse(path)
