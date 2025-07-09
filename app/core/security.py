"""
Security utilities for authentication and authorization.
"""
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings


class SecurityManager:
    """Security operations manager."""

    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.algorithm = "HS256"

    def hash_password(self, password: str) -> str:
        """Hash a password."""
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return self.pwd_context.verify(plain_password, hashed_password)

    def generate_password_reset_token(self, email: str) -> str:
        """Generate a password reset token."""
        expires = datetime.utcnow() + timedelta(hours=24)
        payload = {
            "sub": email,
            "exp": expires,
            "type": "password_reset"
        }
        return jwt.encode(payload, settings.security.secret_key, algorithm=self.algorithm)

    def generate_email_verification_token(self, email: str) -> str:
        """Generate an email verification token."""
        expires = datetime.utcnow() + timedelta(hours=24)
        payload = {
            "sub": email,
            "exp": expires,
            "type": "email_verification"
        }
        return jwt.encode(payload, settings.security.secret_key, algorithm=self.algorithm)

    def verify_token(self, token: str, token_type: str) -> Optional[str]:
        """Verify a token and return the subject (email)."""
        try:
            payload = jwt.decode(
                token,
                settings.security.secret_key,
                algorithms=[self.algorithm]
            )
            email: str = payload.get("sub")
            token_type_in_token: str = payload.get("type")

            if email is None or token_type_in_token != token_type:
                return None

            return email
        except JWTError:
            return None

    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create an access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.security.access_token_expire_minutes)

        to_encode.update({"exp": expire, "type": "access"})
        return jwt.encode(to_encode, settings.security.secret_key, algorithm=self.algorithm)

    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """Create a refresh token."""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=settings.security.refresh_token_expire_days)
        to_encode.update({"exp": expire, "type": "refresh"})
        return jwt.encode(to_encode, settings.security.secret_key, algorithm=self.algorithm)

    def decode_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Decode a JWT token."""
        try:
            payload = jwt.decode(
                token,
                settings.security.secret_key,
                algorithms=[self.algorithm]
            )
            return payload
        except JWTError:
            return None

    def generate_verification_code(self, length: int = 6) -> str:
        """Generate a random verification code."""
        return ''.join(secrets.choice('0123456789') for _ in range(length))

    def generate_secure_token(self, length: int = 32) -> str:
        """Generate a secure random token."""
        return secrets.token_urlsafe(length)


# Global security manager instance
security_manager = SecurityManager()
