"""
Custom exceptions for the AuthKit System.
"""
from fastapi import HTTPException, status


class UserManagementException(Exception):
    """Base exception for user management system."""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class AuthenticationException(UserManagementException):
    """Exception raised for authentication errors."""
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED)


class AuthorizationException(UserManagementException):
    """Exception raised for authorization errors."""
    def __init__(self, message: str = "Access forbidden"):
        super().__init__(message, status.HTTP_403_FORBIDDEN)


class UserNotFoundException(UserManagementException):
    """Exception raised when user is not found."""
    def __init__(self, message: str = "User not found"):
        super().__init__(message, status.HTTP_404_NOT_FOUND)


class UserAlreadyExistsException(UserManagementException):
    """Exception raised when user already exists."""
    def __init__(self, message: str = "User already exists"):
        super().__init__(message, status.HTTP_409_CONFLICT)


class InvalidTokenException(UserManagementException):
    """Exception raised for invalid tokens."""
    def __init__(self, message: str = "Invalid or expired token"):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED)


class EmailNotVerifiedException(UserManagementException):
    """Exception raised when email is not verified."""
    def __init__(self, message: str = "Email not verified"):
        super().__init__(message, status.HTTP_403_FORBIDDEN)


class InvalidCredentialsException(UserManagementException):
    """Exception raised for invalid credentials."""
    def __init__(self, message: str = "Invalid credentials"):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED)


class ValidationException(UserManagementException):
    """Exception raised for validation errors."""
    def __init__(self, message: str = "Validation error"):
        super().__init__(message, status.HTTP_422_UNPROCESSABLE_ENTITY)


class EmailServiceException(UserManagementException):
    """Exception raised for email service errors."""
    def __init__(self, message: str = "Email service error"):
        super().__init__(message, status.HTTP_500_INTERNAL_SERVER_ERROR)


class DatabaseException(UserManagementException):
    """Exception raised for database errors."""
    def __init__(self, message: str = "Database error"):
        super().__init__(message, status.HTTP_500_INTERNAL_SERVER_ERROR)


class RateLimitException(UserManagementException):
    """Exception raised for rate limiting."""
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message, status.HTTP_429_TOO_MANY_REQUESTS)


# HTTP Exception helpers
def create_http_exception(exception: UserManagementException) -> HTTPException:
    """Convert custom exception to HTTPException."""
    return HTTPException(
        status_code=exception.status_code,
        detail=exception.message
    )


# Common HTTP exceptions
CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

INACTIVE_USER_EXCEPTION = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Inactive user"
)

INSUFFICIENT_PERMISSIONS_EXCEPTION = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Insufficient permissions"
)