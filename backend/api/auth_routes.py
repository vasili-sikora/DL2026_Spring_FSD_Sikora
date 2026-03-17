from typing import Any

from fastapi import APIRouter, HTTPException

from app.backend.db.sqlite_conn import SQLiteConnection
from app.backend.models.user import UserCreate, UserLogin
from app.backend.repositories.user_repo import UserRepo
from app.backend.services.user_service import UserService

db: SQLiteConnection = SQLiteConnection()
repo: UserRepo = UserRepo(db)
service: UserService = UserService(repo)

auth_router: APIRouter = APIRouter()


@auth_router.post("/auth/register")
def register_user(payload: UserCreate) -> dict[str, Any]:
    try:
        return service.register_user(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@auth_router.post("/auth/login")
def login_user(payload: UserLogin) -> dict[str, Any]:
    try:
        return service.login_user(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
