#!/usr/bin/env python3
"""
Script to check configuration and environment setup.
"""
import sys
import os
from pathlib import Path

# Add the parent directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from app.core.config import settings
except Exception as e:
    print(f"❌ Failed to load configuration: {e}")
    sys.exit(1)


def check_environment_file():
    """Check if .env file exists and has required variables."""
    env_file = Path(".env")

    print("📁 Environment File Check")
    print("-" * 25)

    if not env_file.exists():
        print("❌ .env file not found")
        print("💡 Copy .env.example to .env and configure it")
        return False

    print("✅ .env file exists")

    # Check for required variables
    required_vars = [
        "DATABASE_URL",
        "SECRET_KEY",
        "MAIL_USERNAME",
        "MAIL_PASSWORD",
        "MAIL_FROM"
    ]

    missing_vars = []
    with open(env_file, 'r') as f:
        content = f.read()
        for var in required_vars:
            if f"{var}=" not in content or f"{var}=" in content and content.split(f"{var}=")[1].split('\n')[
                0].strip() == "":
                missing_vars.append(var)

    if missing_vars:
        print(f"⚠️  Missing or empty variables: {', '.join(missing_vars)}")
        return False

    print("✅ All required variables present")
    return True


def check_database_config():
    """Check database configuration."""
    print("\n🗄️  Database Configuration")
    print("-" * 26)

    try:
        db_url = settings.database.url
        print(f"✅ Database URL: {db_url[:50]}...")

        if "postgresql" not in db_url:
            print("⚠️  Warning: Not using PostgreSQL")

        return True
    except Exception as e:
        print(f"❌ Database config error: {e}")
        return False


def check_email_config():
    """Check email configuration."""
    print("\n📧 Email Configuration")
    print("-" * 22)

    try:
        email_config = settings.email
        print(f"📨 SMTP Server: {email_config.server}:{email_config.port}")
        print(f"👤 Username: {email_config.username}")
        print(f"📤 From Email: {email_config.from_email}")
        print(f"📝 From Name: {email_config.from_name}")

        # Check if credentials look valid
        if not email_config.username or email_config.username == "test@example.com":
            print("⚠️  Warning: Email username not configured")
            return False

        if not email_config.password or email_config.password == "password":
            print("⚠️  Warning: Email password not configured")
            return False

        print("✅ Email configuration looks valid")
        return True

    except Exception as e:
        print(f"❌ Email config error: {e}")
        return False


def check_security_config():
    """Check security configuration."""
    print("\n🔐 Security Configuration")
    print("-" * 25)

    try:
        security_config = settings.security
        print(f"🔑 Secret Key: {'*' * 20}... (length: {len(security_config.secret_key)})")
        print(f"⏰ Access Token Expire: {security_config.access_token_expire_minutes} minutes")
        print(f"🔄 Refresh Token Expire: {security_config.refresh_token_expire_days} days")

        if len(security_config.secret_key) < 32:
            print("⚠️  Warning: Secret key should be at least 32 characters")
            return False

        if "your-super-secret-key" in security_config.secret_key:
            print("⚠️  Warning: Change the default secret key!")
            return False

        print("✅ Security configuration looks good")
        return True

    except Exception as e:
        print(f"❌ Security config error: {e}")
        return False


def check_app_config():
    """Check application configuration."""
    print("\n🚀 Application Configuration")
    print("-" * 29)

    try:
        app_config = settings.app
        print(f"📱 App Name: {app_config.name}")
        print(f"🔢 Version: {app_config.version}")
        print(f"🔧 Debug Mode: {app_config.debug}")
        print(f"🌐 Frontend URL: {app_config.frontend_url}")
        print(f"📍 API Prefix: {app_config.api_prefix}")

        print("✅ Application configuration loaded")
        return True

    except Exception as e:
        print(f"❌ App config error: {e}")
        return False


def check_template_directory():
    """Check if email templates exist."""
    print("\n📄 Template Directory Check")
    print("-" * 26)

    template_dir = Path("app/templates/email")

    if not template_dir.exists():
        print("❌ Email templates directory not found")
        print("💡 Create app/templates/email/ directory")
        return False

    required_templates = [
        "base.html",
        "verification.html",
        "password_reset.html",
        "welcome.html"
    ]

    missing_templates = []
    for template in required_templates:
        if not (template_dir / template).exists():
            missing_templates.append(template)

    if missing_templates:
        print(f"❌ Missing templates: {', '.join(missing_templates)}")
        return False

    print("✅ All required email templates found")
    return True


def main():
    """Main configuration checker."""
    print("FastAPI User Management - Configuration Checker")
    print("=" * 48)

    checks = [
        check_environment_file,
        check_database_config,
        check_email_config,
        check_security_config,
        check_app_config,
        check_template_directory
    ]

    passed = 0
    total = len(checks)

    for check in checks:
        try:
            if check():
                passed += 1
        except Exception as e:
            print(f"❌ Check failed with error: {e}")

    print(f"\n📊 Configuration Check Results")
    print("=" * 32)
    print(f"✅ Passed: {passed}/{total}")

    if passed == total:
        print("🎉 All configuration checks passed!")
        print("🚀 Your system is ready to run!")
    else:
        print("⚠️  Some configuration issues found")
        print("🔧 Please fix the issues above before running the system")

        print("\n💡 Quick fixes:")
        print("1. Copy .env.example to .env")
        print("2. Configure your email settings")
        print("3. Set a secure SECRET_KEY")
        print("4. Update DATABASE_URL if needed")

        return False

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)