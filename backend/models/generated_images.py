from pydantic import BaseModel


class GenerateImageRequest(BaseModel):
    text_top: str = ""
    text_bottom: str = ""
