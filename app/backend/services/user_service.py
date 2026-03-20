from typing import Any

from app.backend.models.user import UserCreate, UserLogin
from app.backend.repositories.user_repo import UserRepo
from app.backend.services.exceptions import (
    InvalidCredentialsError,
    InvalidEmailError,
    InvalidPasswordError,
    InvalidUserContextError,
    UserNotFoundError,
)
from app.backend.utils.password import PasswordHasher, PasswordValidator
from app.backend.utils.validate_email import EmailValidator


class UserService:
    def __init__(self, repo: UserRepo) -> None:
        self._repo = repo

    # def get_password_by_email(self, email: str) -> str:
    #     if not email:
    #         raise ValueError("Invalid email")
    #     password = self._repo.get_password_by_email(email)
    #     return password

    def register_user(self, payload: UserCreate) -> dict[str, Any]:
        if not PasswordValidator.is_valid_password(payload.password):
            raise InvalidPasswordError("Invalid password")
        if not EmailValidator.is_valid_email(payload.email):
            raise InvalidEmailError("Invalid email")
        password = PasswordHasher.hash(payload.password)
        return self._repo.save_user(payload.email, password)

    def login_user(self, payload: UserLogin) -> dict[str, Any]:
        if not PasswordValidator.is_valid_password(payload.password):
            raise InvalidPasswordError("Invalid password")
        if not EmailValidator.is_valid_email(payload.email):
            raise InvalidEmailError("Invalid email")
        if not self._verify_password(payload.email, payload.password):
            raise InvalidCredentialsError("Invalid email or password")
        user = self._repo.login_user(payload.email)
        if not user:
            raise InvalidCredentialsError("Invalid email or password")
        return user

    def _verify_password(self, email: str, password: str) -> bool:
        pswd_hash = self._repo.get_password_by_email(email)
        if not pswd_hash:
            return False

        if not PasswordHasher.verify(password, pswd_hash):
            return False
        return True

    def get_user_by_id(self, user_id: int) -> dict[str, Any]:
        if user_id < 1:
            raise InvalidUserContextError("Invalid user id")

        user = self._repo.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundError("User not found")

        return user
