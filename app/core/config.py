"""
Configuration settings for the FastAPI User Management System.
"""
from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseModel):
    """Database configuration settings."""
    url: str = Field(..., description="Database connection URL")
    test_url: Optional[str] = Field(None, description="Test database connection URL")
    echo: bool = Field(False, description="Enable SQLAlchemy query logging")


class SecuritySettings(BaseModel):
    """Security configuration settings."""
    secret_key: str = Field(..., description="Secret key for JWT tokens")
    access_token_expire_minutes: int = Field(30, description="Access token expiration time in minutes")
    refresh_token_expire_days: int = Field(7, description="Refresh token expiration time in days")
    password_reset_expire_hours: int = Field(24, description="Password reset token expiration time in hours")


class EmailSettings(BaseModel):
    """Email configuration settings."""
    username: EmailStr = Field(..., description="Email username")
    password: str = Field(..., description="Email password")
    from_email: EmailStr = Field(..., description="Default from email")
    from_name: str = Field("FastAPI Users", description="Default from name")
    server: str = Field("smtp.gmail.com", description="SMTP server")
    port: int = Field(587, description="SMTP port")
    tls: bool = Field(True, description="Use TLS")
    ssl: bool = Field(False, description="Use SSL")


class AppSettings(BaseModel):
    """Application configuration settings."""
    name: str = Field("FastAPI User Management", description="Application name")
    version: str = Field("1.0.0", description="Application version")
    debug: bool = Field(False, description="Debug mode")
    api_prefix: str = Field("/api/v1", description="API prefix")
    frontend_url: str = Field("http://localhost:3000", description="Frontend URL")


class Settings(BaseSettings):
    """Main application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Database
    database_url: str = Field(..., env="DATABASE_URL")
    database_test_url: Optional[str] = Field(None, env="DATABASE_TEST_URL")

    # Security
    secret_key: str = Field(..., env="SECRET_KEY")
    access_token_expire_minutes: int = Field(30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(7, env="REFRESH_TOKEN_EXPIRE_DAYS")

    # Email
    mail_username: Optional[EmailStr] = Field(None, env="MAIL_USERNAME")
    mail_password: Optional[str] = Field(None, env="MAIL_PASSWORD")
    mail_from: Optional[EmailStr] = Field(None, env="MAIL_FROM")
    mail_from_name: str = Field("Neubit-AuthKit", env="MAIL_FROM_NAME")
    mail_server: str = Field("smtp.gmail.com", env="MAIL_SERVER")
    mail_port: int = Field(587, env="MAIL_PORT")

    # Redis
    redis_url: str = Field("redis://localhost:6379", env="REDIS_URL")

    # App
    app_name: str = Field("FastAPI User Management", env="APP_NAME")
    app_version: str = Field("1.0.0", env="APP_VERSION")
    debug: bool = Field(False, env="DEBUG")
    api_prefix: str = Field("/api/v1", env="API_PREFIX")
    frontend_url: str = Field("http://localhost:3000", env="FRONTEND_URL")

    @property
    def database(self) -> DatabaseSettings:
        """Get database settings."""
        return DatabaseSettings(
            url=self.database_url,
            test_url=self.database_test_url,
            echo=self.debug
        )

    @property
    def security(self) -> SecuritySettings:
        """Get security settings."""
        return SecuritySettings(
            secret_key=self.secret_key,
            access_token_expire_minutes=self.access_token_expire_minutes,
            refresh_token_expire_days=self.refresh_token_expire_days
        )

    @property
    def email(self) -> EmailSettings:
        """Get email settings."""
        return EmailSettings(
            username=self.mail_username or "test@example.com",
            password=self.mail_password or "password",
            from_email=self.mail_from or self.mail_username or "test@example.com",
            from_name=self.mail_from_name,
            server=self.mail_server,
            port=self.mail_port
        )

    @property
    def app(self) -> AppSettings:
        """Get app settings."""
        return AppSettings(
            name=self.app_name,
            version=self.app_version,
            debug=self.debug,
            api_prefix=self.api_prefix,
            frontend_url=self.frontend_url
        )


# Global settings instance
settings = Settings()