"""
Email service for sending notifications and verification emails.
"""
import logging
from pathlib import Path
from typing import Dict, Any, List

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from jinja2 import Environment, FileSystemLoader

from app.core.config import settings
from app.core.exceptions import EmailServiceException

logger = logging.getLogger(__name__)

# Email templates directory
TEMPLATES_DIR = Path(__file__).parent.parent / "templates" / "email"


class EmailService:
    """Service for sending emails."""

    def __init__(self):
        self.config = ConnectionConfig(
            MAIL_USERNAME=settings.email.username,
            MAIL_PASSWORD=settings.email.password,
            MAIL_FROM=settings.email.from_email,
            MAIL_PORT=settings.email.port,
            MAIL_SERVER=settings.email.server,
            MAIL_FROM_NAME=settings.email.from_name,
            MAIL_STARTTLS=settings.email.tls,
            MAIL_SSL_TLS=settings.email.ssl,
            USE_CREDENTIALS=True,
            VALIDATE_CERTS=True,
            TEMPLATE_FOLDER=str(TEMPLATES_DIR)
        )

        self.fastmail = FastMail(self.config)

        # Setup Jinja2 environment for custom templates
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(TEMPLATES_DIR)),
            autoescape=True
        )

    async def send_email(
            self,
            recipients: List[str],
            subject: str,
            template_name: str,
            template_data: Dict[str, Any],
            attachments: List[str] = None
    ) -> bool:
        """Send email using template."""
        try:
            # Render template
            template = self.jinja_env.get_template(f"{template_name}.html")
            html_content = template.render(**template_data)

            # Create message
            message = MessageSchema(
                subject=subject,
                recipients=recipients,
                body=html_content,
                subtype="html",
                attachments=attachments or []
            )

            # Send email
            await self.fastmail.send_message(message)
            logger.info(f"Email sent successfully to {recipients}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {recipients}: {str(e)}")
            raise EmailServiceException(f"Failed to send email: {str(e)}")

    async def send_verification_email(self, email: str, name: str, token: str) -> bool:
        """Send email verification email."""
        verification_url = f"{settings.app.frontend_url}/verify-email?token={token}"

        template_data = {
            "name": name,
            "verification_url": verification_url,
            "app_name": settings.app.name,
            "frontend_url": settings.app.frontend_url
        }

        return await self.send_email(
            recipients=[email],
            subject="Verify Your Email Address",
            template_name="verification",
            template_data=template_data
        )

    async def send_password_reset_email(self, email: str, name: str, token: str) -> bool:
        """Send password reset email."""
        reset_url = f"{settings.app.frontend_url}/reset-password?token={token}"

        template_data = {
            "name": name,
            "reset_url": reset_url,
            "app_name": settings.app.name,
            "frontend_url": settings.app.frontend_url
        }

        return await self.send_email(
            recipients=[email],
            subject="Reset Your Password",
            template_name="password_reset",
            template_data=template_data
        )

    async def send_welcome_email(self, email: str, name: str) -> bool:
        """Send welcome email to new users."""
        template_data = {
            "name": name,
            "app_name": settings.app.name,
            "frontend_url": settings.app.frontend_url,
            "login_url": f"{settings.app.frontend_url}/login"
        }

        return await self.send_email(
            recipients=[email],
            subject=f"Welcome to {settings.app.name}!",
            template_name="welcome",
            template_data=template_data
        )

    async def send_password_changed_email(self, email: str, name: str) -> bool:
        """Send password changed notification email."""
        template_data = {
            "name": name,
            "app_name": settings.app.name,
            "frontend_url": settings.app.frontend_url,
            "support_email": settings.email.from_email
        }

        return await self.send_email(
            recipients=[email],
            subject="Password Changed Successfully",
            template_name="password_changed",
            template_data=template_data
        )

    async def send_account_locked_email(self, email: str, name: str) -> bool:
        """Send account locked notification email."""
        template_data = {
            "name": name,
            "app_name": settings.app.name,
            "frontend_url": settings.app.frontend_url,
            "support_email": settings.email.from_email
        }

        return await self.send_email(
            recipients=[email],
            subject="Account Security Alert",
            template_name="account_locked",
            template_data=template_data
        )


# Global email service instance
email_service = EmailService()
