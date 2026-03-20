from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Response

from app.backend.auth.cookies import clear_session_cookie, set_session_cookie
from app.backend.auth.dependencies import get_current_user_id
from app.backend.dependencies import user_service as service
from app.backend.models.user import UserCreate, UserLogin

auth_router: APIRouter = APIRouter()


@auth_router.post("/auth/register")
def register_user(payload: UserCreate, response: Response) -> dict[str, Any]:
    try:
        user = service.register_user(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    set_session_cookie(response, user["id"])
    return user


@auth_router.post("/auth/login")
def login_user(payload: UserLogin, response: Response) -> dict[str, Any]:
    try:
        user = service.login_user(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    set_session_cookie(response, user["id"])
    return user


@auth_router.post("/auth/logout")
def logout_user(response: Response) -> dict[str, str]:
    clear_session_cookie(response)
    return {"detail": "Logged out"}


@auth_router.get("/auth/me")
def get_me(current_user_id: int = Depends(get_current_user_id)) -> dict[str, Any]:
    try:
        return service.get_user_by_id(current_user_id)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
