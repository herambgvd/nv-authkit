"""
Configuration settings for the User Management Service
"""
from typing import Optional

from pydantic import BaseModel, EmailStr, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseModel):
    """
    Database Configuration settings
    """
    url: str = Field(..., description="Database URL")
    test_url: Optional[str] = Field(None, description="Test Database URL")
    echo: bool = Field(False, description="SQLAlchemy Query Logging")


class SecuritySettings(BaseModel):
    """
    Security Configuration settings
    """
    secret_key: str = Field(..., description="Secret key for JWT token")
    access_token_expire_minutes: int = Field(30, description="Access Token Expiration time in minutes")
    refresh_token_expire_days: int = Field(7, description="Refresh Token Expiration time in days")
    password_reset_expire_hours: int = Field(24, description="Password Reset Expiration time in hours")


class EmailSettings(BaseModel):
    """
    Email Configuration settings
    """
    username: EmailStr = Field(..., description="Email Username")
    password: str = Field(..., description="Email Password")
    from_email: EmailStr = Field(..., description="Default From Email")
    from_name: str = Field("Users", description="Default From Name")
    server: str = Field("smtp.gmail.com", description="STMP Server")
    port: int = Field(587, description="STMP Server port")
    tls: bool = Field(True, description="STMP Server TLS mode")
    ssl: bool = Field(False, description="STMP Server SSL mode")


class Settings(BaseSettings):
    """
    Application settings
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        exclude="ignore"
    )
    # Database
    database_url: str = Field(..., env="DATABASE_URL")
    database_test_url: Optional[str] = Field(None, env="DATABASE_TEST_URL")

    # Security
    secret_key: str = Field(..., env="SECRET_KEY")
    access_token_expire_minutes: int = Field(30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(7, env="REFRESH_TOKEN_EXPIRE_DAYS")

    # Email
    mail_username: EmailStr = Field(..., env="MAIL_USERNAME")
    mail_password: str = Field(..., env="MAIL_PASSWORD")
    mail_from: EmailStr = Field(..., env="MAIL_FROM")
    mail_from_name: str = Field("FastAPI Users", env="MAIL_FROM_NAME")
    mail_server: str = Field("smtp.gmail.com", env="MAIL_SERVER")
    mail_port: int = Field(587, env="MAIL_PORT")

    # Redis
    redis_url: str = Field("redis://localhost:6379", env="REDIS_URL")

    # App
    app_name: str = Field("Auth Kit", env="APP_NAME")
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
            username=self.mail_username,
            password=self.mail_password,
            from_email=self.mail_from,
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


# Global Settings Instance
settings = Settings()
