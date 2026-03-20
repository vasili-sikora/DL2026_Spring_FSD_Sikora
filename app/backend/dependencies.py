from app.backend.db.sqlite_conn import SQLiteConnection
from app.backend.repositories.generated_images_repo import GeneratedImagesRepository
from app.backend.repositories.templates_repo import TemplateRepository
from app.backend.repositories.user_repo import UserRepo
from app.backend.services.generated_images_service import GeneratedImagesService
from app.backend.services.templates_service import TemplateService
from app.backend.services.user_service import UserService

db = SQLiteConnection()

user_repo = UserRepo(db)
template_repo = TemplateRepository(db)
generated_images_repo = GeneratedImagesRepository(db)

user_service = UserService(user_repo)
template_service = TemplateService(template_repo)
generated_images_service = GeneratedImagesService(generated_images_repo, template_repo)
