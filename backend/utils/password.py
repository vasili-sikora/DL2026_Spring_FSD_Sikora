from passlib.context import CryptContext


class PasswordHasher:
    pwd_context: CryptContext = CryptContext(schemes=["bcrypt"], deprecated="auto")

    @staticmethod
    def hash(password: str) -> str:
        return PasswordHasher.pwd_context.hash(password)

    @staticmethod
    def verify(password: str, password_hash: str) -> bool:
        return PasswordHasher.pwd_context.verify(password, password_hash)


class PasswordValidator:
    @staticmethod
    def is_valid_password(password: str) -> bool:
        if not password:
            return False
        if len(password) < 8:
            return False

        return True
