from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from starlette.responses import FileResponse

from app.backend.auth.dependencies import get_current_user_id
from app.backend.core.config import BASE_DIR
from app.backend.core.rate_limit import limiter
from app.backend.dependencies import generated_images_service
from app.backend.models.generated_images import (
    ErrorResponse,
    GeneratedImageResponse,
    GenerateImageRequest,
    PreviewImageRequest,
)
from app.backend.services.exceptions import (
    ImageGenerationValidationError,
    ImageNotFoundError,
    ImagePersistenceError,
    TemplateFontError,
    TemplateImageFileNotFoundError,
    TemplateImageFormatError,
    TemplateNotFoundError,
)

generated_images_router: APIRouter = APIRouter()


@generated_images_router.get("/generated_images")
def get_images(
    current_user_id: int = Depends(get_current_user_id),
) -> list[dict[str, Any]]:
    try:
        images = generated_images_service.get_all_images(current_user_id)
    except ImageNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return [dict(image) for image in images]


@generated_images_router.get(
    "/generated_images/{image_id}",
    response_model=GeneratedImageResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Image not found"},
    },
)
def get_image_by_id(
    image_id: int, current_user_id: int = Depends(get_current_user_id)
) -> GeneratedImageResponse:
    try:
        image = generated_images_service.get_image_by_id(image_id, current_user_id)
    except ImageNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return GeneratedImageResponse(**dict(image))


@generated_images_router.post(
    "/templates/{template_id}/generate",
    response_model=GeneratedImageResponse,
    responses={
        400: {
            "model": ErrorResponse,
            "description": "Template image format/font is not supported",
        },
        404: {
            "model": ErrorResponse,
            "description": "Template or template image file not found",
        },
    },
)
@limiter.limit("10/minute")
def generate_image(
    request: Request,
    template_id: int,
    payload: GenerateImageRequest,
    current_user_id: int = Depends(get_current_user_id),
) -> GeneratedImageResponse:
    try:
        image = generated_images_service.generate_image(
            template_id, payload, current_user_id
        )
    except TemplateNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except TemplateImageFileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except TemplateImageFormatError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except TemplateFontError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ImagePersistenceError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return GeneratedImageResponse(**dict(image))


@generated_images_router.post(
    "/templates/{template_id}/preview",
    responses={
        200: {"description": "Rendered preview image (JPEG)"},
        400: {
            "model": ErrorResponse,
            "description": "Template image format/font is not supported",
        },
        404: {
            "model": ErrorResponse,
            "description": "Template or template image file not found",
        },
    },
)
@limiter.limit("50/minute")
def preview_image(
    request: Request, template_id: int, payload: PreviewImageRequest
) -> Response:
    try:
        image_bytes = generated_images_service.preview_image(template_id, payload)
    except TemplateNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except TemplateImageFileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except TemplateImageFormatError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except TemplateFontError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ImageGenerationValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return Response(content=image_bytes, media_type="image/jpeg")


@generated_images_router.get("/images/{share_token}")
def get_image_by_share_token(share_token: str) -> FileResponse:
    try:
        image = generated_images_service.get_image_by_share_token(share_token)
    except ImageNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    path = BASE_DIR / image["image_path"]

    return FileResponse(path)
