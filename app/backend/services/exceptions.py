class DomainError(Exception):
    pass


class AppValidationError(DomainError):
    pass


class AuthenticationError(DomainError):
    pass


class AuthorizationError(DomainError):
    pass


class ImageNotFoundError(Exception):
    pass


class TemplateNotFoundError(Exception):
    pass


class TemplateImageFileNotFoundError(Exception):
    pass


class TemplateImageFormatError(Exception):
    pass


class TemplateFontError(Exception):
    pass


class InvalidEmailError(AuthenticationError):
    pass


class InvalidPasswordError(AuthenticationError):
    pass


class InvalidCredentialsError(AuthenticationError):
    pass


class UserAlreadyExistsError(AuthenticationError):
    pass


class UserNotFoundError(AuthenticationError):
    pass


class InvalidUserContextError(AuthenticationError):
    pass


class AdminAccessRequiredError(AuthorizationError):
    pass


class TemplateValidationError(AppValidationError):
    pass


class ImageGenerationValidationError(AppValidationError):
    pass


class ImagePersistenceError(DomainError):
    pass
