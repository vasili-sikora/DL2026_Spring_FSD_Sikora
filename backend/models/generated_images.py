from datetime import datetime

from pydantic import BaseModel


class GenerateImageRequest(BaseModel):
    text_top: str = ""
    text_bottom: str = ""


class GeneratedImageResponse(BaseModel):
    id: int
    template_id: int
    text_top: str | None = None
    text_bottom: str | None = None
    image_path: str
    share_token: str
    created_at: datetime


class ErrorResponse(BaseModel):
    detail: str
