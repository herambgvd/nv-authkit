#!/usr/bin/env python3
"""
Script to test email configuration and sending.
"""
import asyncio
import sys
import os

# Add the parent directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.email_service import email_service
from app.core.config import settings


async def test_email_configuration():
    """Test email configuration and sending."""
    print("Testing Email Configuration")
    print("=" * 30)
    print(f"SMTP Server: {settings.email.server}")
    print(f"SMTP Port: {settings.email.port}")
    print(f"From Email: {settings.email.from_email}")
    print(f"Username: {settings.email.username}")
    print("=" * 30)

    test_email = input("Enter test email address: ").strip()
    if not test_email:
        print("❌ Email address is required!")
        return

    try:
        print("📧 Sending test verification email...")

        success = await email_service.send_verification_email(
            email=test_email,
            name="Test User",
            token="test_verification_token_123"
        )

        if success:
            print("✅ Test email sent successfully!")
            print(f"📬 Check your inbox at {test_email}")
        else:
            print("❌ Failed to send test email")

    except Exception as e:
        print(f"❌ Error sending email: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Check your email credentials in .env file")
        print("2. Verify SMTP server settings")
        print("3. Ensure 'less secure apps' is enabled (Gmail)")
        print("4. Use app-specific password (Gmail with 2FA)")
        print("5. Check firewall/network settings")


async def test_template_rendering():
    """Test template rendering without sending email."""
    print("\n🎨 Testing Template Rendering...")

    try:
        # Test template rendering
        template_data = {
            "name": "Test User",
            "verification_url": "https://example.com/verify?token=test123",
            "app_name": settings.app.name,
            "frontend_url": settings.app.frontend_url
        }

        template = email_service.jinja_env.get_template("verification.html")
        html_content = template.render(**template_data)

        print("✅ Template rendered successfully!")
        print(f"📄 Content length: {len(html_content)} characters")

        # Save rendered template for inspection
        with open("test_email_output.html", "w", encoding="utf-8") as f:
            f.write(html_content)

        print("💾 Rendered template saved to: test_email_output.html")

    except Exception as e:
        print(f"❌ Template rendering error: {e}")


async def main():
    """Main function."""
    print("FastAPI User Management - Email Testing Tool")
    print("=" * 45)

    # Test template rendering first
    await test_template_rendering()

    # Test email configuration
    test_type = input("\nDo you want to send a test email? (y/n): ").strip().lower()

    if test_type == 'y':
        await test_email_configuration()
    else:
        print("Skipping email sending test.")

    print("\n✨ Email testing completed!")


if __name__ == "__main__":
    asyncio.run(main())