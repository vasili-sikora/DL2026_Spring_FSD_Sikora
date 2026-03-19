class EmailValidator:
    @staticmethod
    def is_valid_email(email: str) -> bool:
        if not email:
            return False
        if "@" not in email:
            return False
        return True
