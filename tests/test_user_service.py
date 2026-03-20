import pytest

from app.backend.models.user import UserCreate, UserLogin
from app.backend.services.exceptions import (
    InvalidCredentialsError,
    InvalidEmailError,
    InvalidPasswordError,
)
from app.backend.services.user_service import UserService
from app.backend.utils.password import PasswordHasher


class FakeUserRepo:
    def __init__(self) -> None:
        self.passwords_by_email: dict[str, str] = {}
        self.users_by_email: dict[str, dict[str, object]] = {}
        self.saved_payloads: list[tuple[str, str]] = []

    def get_password_by_email(self, email: str) -> str | None:
        return self.passwords_by_email.get(email)

    def save_user(self, email: str, password: str) -> dict[str, object]:
        self.saved_payloads.append((email, password))
        user = {"id": 1, "email": email, "is_admin": 0}
        self.users_by_email[email] = user
        self.passwords_by_email[email] = password
        return user

    def login_user(self, email: str) -> dict[str, object] | None:
        return self.users_by_email.get(email)

    def get_user_by_id(self, user_id: int) -> dict[str, object] | None:
        for user in self.users_by_email.values():
            if user["id"] == user_id:
                return user
        return None


def test_register_rejects_invalid_email() -> None:
    service = UserService(FakeUserRepo())

    with pytest.raises(InvalidEmailError, match="Invalid email"):
        service.register_user(UserCreate(email="not-an-email", password="abcd1234"))


@pytest.mark.parametrize("password", ["", "short", "1234567"])
def test_register_rejects_too_short_password(password: str) -> None:
    service = UserService(FakeUserRepo())

    with pytest.raises(InvalidPasswordError, match="Invalid password"):
        service.register_user(UserCreate(email="user@example.com", password=password))


def test_register_accepts_unicode_and_emoji_password() -> None:
    repo = FakeUserRepo()
    service = UserService(repo)
    raw_password = "ПароЛь😀12345"

    result = service.register_user(
        UserCreate(email="unicode.user@example.com", password=raw_password)
    )

    assert result["email"] == "unicode.user@example.com"
    assert len(repo.saved_payloads) == 1
    _, hashed_password = repo.saved_payloads[0]
    assert hashed_password != raw_password
    assert PasswordHasher.verify(raw_password, hashed_password) is True


def test_register_surfaces_password_hasher_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = UserService(FakeUserRepo())

    def fake_hash(_: str) -> str:
        raise ValueError("password cannot be longer than 72 bytes")

    monkeypatch.setattr(PasswordHasher, "hash", staticmethod(fake_hash))

    with pytest.raises(ValueError, match="longer than 72 bytes"):
        service.register_user(
            UserCreate(email="long.password@example.com", password="abcd1234")
        )


def test_login_success() -> None:
    repo = FakeUserRepo()
    password = "abcd1234"
    repo.passwords_by_email["user@example.com"] = PasswordHasher.hash(password)
    repo.users_by_email["user@example.com"] = {
        "id": 42,
        "email": "user@example.com",
        "is_admin": 0,
    }
    service = UserService(repo)

    result = service.login_user(UserLogin(email="user@example.com", password=password))

    assert result["id"] == 42
    assert result["email"] == "user@example.com"


def test_login_rejects_invalid_password() -> None:
    repo = FakeUserRepo()
    repo.passwords_by_email["user@example.com"] = PasswordHasher.hash("abcd1234")
    repo.users_by_email["user@example.com"] = {
        "id": 42,
        "email": "user@example.com",
        "is_admin": 0,
    }
    service = UserService(repo)

    with pytest.raises(InvalidCredentialsError, match="Invalid email or password"):
        service.login_user(UserLogin(email="user@example.com", password="abcd1235"))


def test_login_rejects_invalid_email_format() -> None:
    service = UserService(FakeUserRepo())

    with pytest.raises(InvalidEmailError, match="Invalid email"):
        service.login_user(UserLogin(email="invalid-email", password="abcd1234"))


def test_login_rejects_unknown_email() -> None:
    service = UserService(FakeUserRepo())

    with pytest.raises(InvalidCredentialsError, match="Invalid email or password"):
        service.login_user(UserLogin(email="ghost@example.com", password="abcd1234"))
