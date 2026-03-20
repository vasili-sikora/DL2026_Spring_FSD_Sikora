from pathlib import Path

import pytest

from app.backend.core.config import BASE_DIR
from app.backend.storage.paths import resolve_storage_path
from app.backend.utils.password import PasswordHasher, PasswordValidator
from app.backend.utils.validate_email import EmailValidator


def test_password_hasher_roundtrip_with_unicode() -> None:
    raw_password = "Пароль😀1234"
    hashed = PasswordHasher.hash(raw_password)

    assert hashed != raw_password
    assert PasswordHasher.verify(raw_password, hashed) is True
    assert PasswordHasher.verify("wrong-password", hashed) is False


@pytest.mark.parametrize(
    "password, expected",
    [
        ("", False),
        ("1234567", False),
        ("12345678", True),
        ("😀😀😀😀😀😀😀😀", True),
    ],
)
def test_password_validator(password: str, expected: bool) -> None:
    assert PasswordValidator.is_valid_password(password) is expected


@pytest.mark.parametrize(
    "email, expected",
    [
        ("", False),
        ("not-an-email", False),
        ("user@example.com", True),
        ("emoji😀@example.com", True),
    ],
)
def test_email_validator(email: str, expected: bool) -> None:
    assert EmailValidator.is_valid_email(email) is expected


def test_resolve_storage_path_absolute(tmp_path: Path) -> None:
    absolute_path = tmp_path / "file.jpg"
    absolute_path.write_bytes(b"x")

    resolved = resolve_storage_path(absolute_path)

    assert resolved == absolute_path


def test_resolve_storage_path_relative() -> None:
    relative = Path("data/templates/template.jpg")

    resolved = resolve_storage_path(relative)

    assert resolved == BASE_DIR / relative
