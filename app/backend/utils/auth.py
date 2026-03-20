from fastapi import Cookie, HTTPException

from app.backend.utils.session import SESSION_COOKIE_NAME, read_session_token


def get_current_user_id(
    session_token: str | None = Cookie(default=None, alias=SESSION_COOKIE_NAME),
) -> int:
    if not session_token:
        raise HTTPException(status_code=401, detail="Authentication required")

    user_id = read_session_token(session_token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired session")

    return user_id
