from pydantic import BaseModel


class TemplateCreate(BaseModel):
    name: str
    image_name: str
