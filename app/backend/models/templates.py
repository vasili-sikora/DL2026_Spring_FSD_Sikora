from pydantic import BaseModel, Field


class TemplateCreate(BaseModel):
    name: str
    image_name: str


class TemplateLayoutUpdate(BaseModel):
    top_text_x: int = Field(ge=0)
    top_text_y: int = Field(ge=0)
    top_text_width: int = Field(gt=0)
    bottom_text_x: int = Field(ge=0)
    bottom_text_y: int = Field(ge=0)
    bottom_text_width: int = Field(gt=0)


class TemplateLayoutPreviewRequest(TemplateLayoutUpdate):
    sample_text_top: str = "TOP TEXT"
    sample_text_bottom: str = "BOTTOM TEXT"
    font_name: str = "dejavu_sans"
    font_size: int = Field(default=40, ge=12, le=120)
    font_color: str = Field(default="#ffffff", pattern=r"^#[0-9A-Fa-f]{6}$")
