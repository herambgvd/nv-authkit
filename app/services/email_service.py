"""
Email service for sending notifications and verification emails.
"""
import logging
from typing import Dict, Any, List
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from jinja2 import Environment, FileSystemLoader
from pathlib import Path

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

    async def send_role_assigned_email(self, email: str, name: str, role_name: str, permissions: list = None, assigned_by: str = None) -> bool:
        """Send role assignment notification email."""
        template_data = {
            "name": name,
            "role_name": role_name,
            "permissions": permissions or [],
            "assigned_by": assigned_by or "System Administrator",
            "assigned_date": datetime.now().strftime("%B %d, %Y at %I:%M %p"),
            "app_name": settings.app.name,
            "frontend_url": settings.app.frontend_url,
            "support_email": settings.email.from_email
        }

        return await self.send_email(
            recipients=[email],
            subject=f"New Role Assigned - {settings.app.name}",
            template_name="role_assigned",
            template_data=template_data
        )

    async def send_login_alert_email(self, email: str, name: str, login_details: dict) -> bool:
        """Send login alert notification email."""
        template_data = {
            "name": name,
            "login_time": login_details.get("time", "Unknown"),
            "ip_address": login_details.get("ip", "Unknown"),
            "location": login_details.get("location", "Unknown"),
            "device_info": login_details.get("device", "Unknown"),
            "browser_info": login_details.get("browser", "Unknown"),
            "is_suspicious": login_details.get("suspicious", False),
            "recent_logins": login_details.get("recent_logins", []),
            "app_name": settings.app.name,
            "frontend_url": settings.app.frontend_url,
            "support_email": settings.email.from_email
        }

        subject = "🚨 Suspicious Login Alert" if login_details.get("suspicious") else "New Login Alert"

        return await self.send_email(
            recipients=[email],
            subject=f"{subject} - {settings.app.name}",
            template_name="login_alert",
            template_data=template_data
        )

    async def send_data_export_email(self, email: str, name: str, export_details: dict) -> bool:
        """Send data export ready notification email."""
        template_data = {
            "name": name,
            "download_url": export_details.get("download_url"),
            "request_date": export_details.get("request_date"),
            "completion_date": export_details.get("completion_date"),
            "file_format": export_details.get("file_format", "ZIP"),
            "file_size": export_details.get("file_size", "Unknown"),
            "expiry_date": export_details.get("expiry_date"),
            "expiry_hours": export_details.get("expiry_hours", 48),
            "app_name": settings.app.name,
            "frontend_url": settings.app.frontend_url,
            "support_email": settings.email.from_email
        }

        return await self.send_email(
            recipients=[email],
            subject=f"Your Data Export is Ready - {settings.app.name}",
            template_name="data_export",
            template_data=template_data
        )

    async def send_newsletter_email(self, email: str, name: str, newsletter_data: dict) -> bool:
        """Send newsletter email."""
        template_data = {
            "name": name,
            "newsletter_title": newsletter_data.get("title", "Newsletter"),
            "newsletter_subtitle": newsletter_data.get("subtitle"),
            "newsletter_intro": newsletter_data.get("intro"),
            "featured_content": newsletter_data.get("featured_content"),
            "primary_cta": newsletter_data.get("primary_cta"),
            "news_items": newsletter_data.get("news_items", []),
            "product_updates": newsletter_data.get("product_updates", []),
            "community_highlights": newsletter_data.get("community_highlights", []),
            "tips_section": newsletter_data.get("tips_section"),
            "upcoming_events": newsletter_data.get("upcoming_events", []),
            "stats_section": newsletter_data.get("stats_section", []),
            "unsubscribe_url": f"{settings.app.frontend_url}/unsubscribe?email={email}",
            "app_name": settings.app.name,
            "frontend_url": settings.app.frontend_url
        }

        return await self.send_email(
            recipients=[email],
            subject=newsletter_data.get("subject", f"Newsletter - {settings.app.name}"),
            template_name="newsletter",
            template_data=template_data
        )


# Global email service instance
email_service = EmailService()