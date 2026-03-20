from typing import Any

from fastapi import Cookie, Depends, HTTPException

from app.backend.auth.session import read_session_token
from app.backend.core.config import SESSION_COOKIE_NAME
from app.backend.dependencies import user_service
from app.backend.services.exceptions import UserNotFoundError


def get_current_user_id(
    session_token: str | None = Cookie(default=None, alias=SESSION_COOKIE_NAME),
) -> int:
    if not session_token:
        raise HTTPException(status_code=401, detail="Authentication required")

    user_id = read_session_token(session_token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired session")

    return user_id


def get_current_user(
    current_user_id: int = Depends(get_current_user_id),
) -> dict[str, Any]:
    try:
        return user_service.get_user_by_id(current_user_id)
    except UserNotFoundError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc


def require_admin(
    current_user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, Any]:
    if not current_user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user
