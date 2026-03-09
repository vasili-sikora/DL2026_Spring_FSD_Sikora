from fastapi import FastAPI

from app.backend.api.routes import router

app = FastAPI()

app.include_router(router)
