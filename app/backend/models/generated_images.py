from datetime import datetime

from pydantic import BaseModel, Field


class GenerateImageRequest(BaseModel):
    text_top: str = ""
    text_bottom: str = ""
    font_name: str = "dejavu_sans"
    font_size: int = Field(default=40, ge=12, le=120)
    font_color: str = Field(default="#ffffff", pattern=r"^#[0-9A-Fa-f]{6}$")


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


class PreviewImageRequest(BaseModel):
    text_top: str = ""
    text_bottom: str = ""
    font_name: str = "dejavu_sans"
    font_size: int = Field(default=40, ge=12, le=120)
    font_color: str = Field(default="#ffffff", pattern=r"^#[0-9A-Fa-f]{6}$")
