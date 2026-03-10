from fastapi import APIRouter

from app.backend.db.sqlite_conn import SQLiteConnection
from app.backend.repositories.generated_images.generated_images_repo import GeneratedImagesRepository
from app.backend.services.generated_images_service import GeneratedImagesService

generated_images_router = APIRouter()

db = SQLiteConnection()
generated_images_repo = GeneratedImagesRepository(db)
generated_images_service = GeneratedImagesService(generated_images_repo)




@generated_images_router.get("/generated_images")
def get_images():
    images = generated_images_service.get_all_images()

    return [dict(image) for image in images]
     
@generated_images_router.get("/generated_images/{image_id}")
def get_image_by_id(image_id: int):
    image = generated_images_service.get_image_by_id(image_id)

    return dict(image) if image else None
