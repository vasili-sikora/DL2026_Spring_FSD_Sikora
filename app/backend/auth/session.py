from itsdangerous import BadSignature, SignatureExpired
from itsdangerous.url_safe import URLSafeTimedSerializer

from app.backend.core.config import (
    SESSION_COOKIE_NAME,
    SESSION_MAX_AGE_SECONDS,
    SESSION_SECRET_KEY,
)

_serializer = URLSafeTimedSerializer(SESSION_SECRET_KEY, salt=SESSION_COOKIE_NAME)


def create_session_token(user_id: int) -> str:
    return _serializer.dumps({"user_id": user_id})


def read_session_token(token: str) -> int | None:
    try:
        data = _serializer.loads(token, max_age=SESSION_MAX_AGE_SECONDS)
    except (BadSignature, SignatureExpired):
        return None

    user_id = data.get("user_id")
    if not isinstance(user_id, int) or user_id < 1:
        return None
    return user_id
