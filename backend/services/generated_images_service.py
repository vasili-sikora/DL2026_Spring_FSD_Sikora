class GeneratedImagesService:
    def __init__(self, repo):
        self.repo = repo

    def get_all_images(self):
        return self.repo.get_all_images()

    def get_image_by_id(self, image_id: int):
        return self.repo.get_image_by_id(image_id)