import pytest
from fastapi import HTTPException

from app.backend.utils.auth import get_current_user_id
from app.backend.utils.session import create_session_token


def test_get_current_user_id_accepts_valid_session_cookie() -> None:
    assert get_current_user_id(create_session_token(17)) == 17


@pytest.mark.parametrize(
    "authorization",
    [
        None,
        "",
        "abc",
        "user-7",
    ],
)
def test_get_current_user_id_rejects_invalid_tokens(
    authorization: str | None,
) -> None:
    with pytest.raises(HTTPException) as exc_info:
        get_current_user_id(authorization)

    assert exc_info.value.status_code == 401
