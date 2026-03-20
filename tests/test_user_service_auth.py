from app.backend.models.user import UserCreate, UserLogin
from app.backend.services.user_service import UserService


class _Repo:
    @staticmethod
    def save_user(email: str, _password: str) -> dict[str, int | str]:
        return {"id": 3, "email": email, "is_admin": 0}

    @staticmethod
    def login_user(email: str) -> dict[str, int | str]:
        return {"id": 4, "email": email, "is_admin": 0}

    @staticmethod
    def get_password_by_email(_email: str) -> str:
        return "$argon2id$v=19$m=65536,t=3,p=4$P4gg+VC4trKx4JkZka1wXg$7i8bD2kcw+UO3QgwjjAF6QjpIDk6yXlCqUI7b3uVe0Q"

    @staticmethod
    def get_user_by_id(user_id: int) -> dict[str, int | str]:
        return {"id": user_id, "email": "user@example.com", "is_admin": 0}

    @staticmethod
    def get_user_by_email(email: str) -> dict[str, int | str]:
        return {"id": 4, "email": email, "is_admin": 0}

    @staticmethod
    def set_admin_status(user_id: int, is_admin: bool) -> dict[str, int | str]:
        return {
            "id": user_id,
            "email": "user@example.com",
            "is_admin": int(is_admin),
        }


def test_register_user_returns_user_payload() -> None:
    service = UserService(_Repo())

    result = service.register_user(
        UserCreate(email="user@example.com", password="abcd1234")
    )

    assert result["id"] == 3
    assert result["email"] == "user@example.com"


def test_login_user_returns_user_payload(monkeypatch) -> None:
    service = UserService(_Repo())
    monkeypatch.setattr(
        service,
        "_verify_password",
        lambda _email, _password: True,
    )

    result = service.login_user(
        UserLogin(email="user@example.com", password="abcd1234")
    )

    assert result["id"] == 4
    assert result["email"] == "user@example.com"


def test_get_user_by_id_returns_user() -> None:
    service = UserService(_Repo())

    result = service.get_user_by_id(4)

    assert result["id"] == 4
    assert result["email"] == "user@example.com"
