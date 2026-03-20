from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Response

from app.backend.core.config import SESSION_COOKIE_SAMESITE, SESSION_COOKIE_SECURE
from app.backend.db.sqlite_conn import SQLiteConnection
from app.backend.models.user import UserCreate, UserLogin
from app.backend.repositories.user_repo import UserRepo
from app.backend.services.user_service import UserService
from app.backend.utils.auth import get_current_user_id
from app.backend.utils.session import (
    SESSION_COOKIE_NAME,
    SESSION_MAX_AGE_SECONDS,
    create_session_token,
)

db: SQLiteConnection = SQLiteConnection()
repo: UserRepo = UserRepo(db)
service: UserService = UserService(repo)

auth_router: APIRouter = APIRouter()


def _set_session_cookie(response: Response, user_id: int) -> None:
    token = create_session_token(user_id)
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=token,
        httponly=True,
        samesite=SESSION_COOKIE_SAMESITE,
        secure=SESSION_COOKIE_SECURE,
        max_age=SESSION_MAX_AGE_SECONDS,
        path="/",
    )


@auth_router.post("/auth/register")
def register_user(payload: UserCreate, response: Response) -> dict[str, Any]:
    try:
        user = service.register_user(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    _set_session_cookie(response, user["id"])
    return user


@auth_router.post("/auth/login")
def login_user(payload: UserLogin, response: Response) -> dict[str, Any]:
    try:
        user = service.login_user(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    _set_session_cookie(response, user["id"])
    return user


@auth_router.post("/auth/logout")
def logout_user(response: Response) -> dict[str, str]:
    response.delete_cookie(key=SESSION_COOKIE_NAME, path="/")
    return {"detail": "Logged out"}


@auth_router.get("/auth/me")
def get_me(current_user_id: int = Depends(get_current_user_id)) -> dict[str, Any]:
    try:
        return service.get_user_by_id(current_user_id)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
