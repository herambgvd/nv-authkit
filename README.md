# AuthKit System

A production-ready, modular user management system built with FastAPI, PostgreSQL, and async support. This system provides comprehensive user authentication, authorization, and management features suitable for enterprise applications.

## 🚀 Features

### Core Features
- **User Registration & Authentication** - Secure user registration with email verification
- **JWT Token Management** - Access and refresh token handling
- **Password Management** - Secure password hashing, reset, and change functionality
- **Email Verification** - Email-based account verification system
- **User Profiles** - Comprehensive user profile management
- **Admin Panel** - Full administrative controls for user management

### Security Features
- **Async PostgreSQL** - High-performance async database operations
- **JWT Authentication** - Secure token-based authentication
- **Password Hashing** - Bcrypt password hashing
- **Email Integration** - Full email notification system
- **Input Validation** - Comprehensive request validation with Pydantic
- **CORS Support** - Configurable cross-origin resource sharing

### Production Ready
- **Docker Support** - Complete containerization with Docker Compose
- **Health Checks** - Comprehensive health monitoring endpoints
- **Database Migrations** - Alembic-based database versioning
- **Logging** - Structured logging for monitoring
- **Environment Configuration** - Flexible configuration management
- **API Documentation** - Auto-generated OpenAPI/Swagger docs

## 📋 Requirements

- Python 3.11+
- PostgreSQL 13+
- Redis 6+ (optional, for caching)
- SMTP server (for email notifications)

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd fastapi-user-management
```

### 2. Environment Setup

Create a `.env` file from the example:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/fastapi_users

# Security
SECRET_KEY=your-super-secret-key-change-this-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Email Configuration
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_FROM=your-email@gmail.com
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587

# App Configuration
APP_NAME=FastAPI User Management
DEBUG=True
FRONTEND_URL=http://localhost:3000
```

### 3. Installation Methods

#### Method A: Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Initialize database
python scripts/init_db.py

# Run migrations
alembic upgrade head

# Create superuser
python scripts/create_superuser.py

# Start development server
uvicorn app.main:app --reload
```

#### Method B: Docker Development

```bash
# Start services
docker-compose -f docker/docker-compose.yml up -d

# Run migrations
docker-compose -f docker/docker-compose.yml exec api alembic upgrade head

# Create superuser
docker-compose -f docker/docker-compose.yml exec api python scripts/create_superuser.py
```

## 🏃‍♂️ Quick Start

### 1. Start the Application

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### 2. API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### 3. Health Check

```bash
curl http://localhost:8000/health
```

## 📚 API Endpoints

### Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register new user |
| POST | `/api/v1/auth/login` | User login |
| POST | `/api/v1/auth/refresh` | Refresh access token |
| POST | `/api/v1/auth/verify-email` | Verify email address |
| POST | `/api/v1/auth/resend-verification` | Resend verification email |
| POST | `/api/v1/auth/forgot-password` | Request password reset |
| POST | `/api/v1/auth/reset-password` | Reset password |
| POST | `/api/v1/auth/change-password` | Change password |
| GET | `/api/v1/auth/me` | Get current user |

### User Management Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/users/profile` | Get user profile |
| PUT | `/api/v1/users/profile` | Update user profile |
| DELETE | `/api/v1/users/profile` | Delete user account |
| GET | `/api/v1/users/` | List users (Admin) |
| GET | `/api/v1/users/{user_id}` | Get user by ID (Admin) |
| PUT | `/api/v1/users/{user_id}` | Update user (Admin) |
| DELETE | `/api/v1/users/{user_id}` | Delete user (Admin) |
| GET | `/api/v1/users/stats/overview` | Get user statistics (Admin) |

### Health Check Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | General health check |
| GET | `/health/db` | Database health check |
| GET | `/health/ready` | Readiness probe |
| GET | `/health/live` | Liveness probe |

## 🏗️ Project Structure

```
fastapi-user-management/
├── app/
│   ├── api/                    # API route handlers
│   │   ├── auth.py            # Authentication endpoints
│   │   ├── users.py           # User management endpoints
│   │   └── health.py          # Health check endpoints
│   ├── core/                  # Core functionality
│   │   ├── config.py          # Configuration settings
│   │   ├── database.py        # Database connection
│   │   ├── security.py        # Security utilities
│   │   └── exceptions.py      # Custom exceptions
│   ├── models/                # SQLAlchemy models
│   │   ├── base.py            # Base model class
│   │   └── user.py            # User model
│   ├── schemas/               # Pydantic schemas
│   │   ├── auth.py            # Authentication schemas
│   │   └── user.py            # User schemas
│   ├── services/              # Business logic layer
│   │   ├── auth_service.py    # Authentication service
│   │   ├── user_service.py    # User service
│   │   └── email_service.py   # Email service
│   ├── dependencies/          # FastAPI dependencies
│   │   └── auth.py            # Authentication dependencies
│   ├── utils/                 # Utility functions
│   └── main.py                # FastAPI application
├── migrations/                # Alembic migrations
├── scripts/                   # Utility scripts
├── tests/                     # Test suite
├── docker/                    # Docker configuration
└── requirements.txt           # Python dependencies
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection URL | Required |
| `SECRET_KEY` | JWT secret key | Required |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration time | 30 |
| `MAIL_USERNAME` | SMTP username | Required |
| `MAIL_PASSWORD` | SMTP password | Required |
| `MAIL_FROM` | From email address | Required |
| `REDIS_URL` | Redis connection URL | redis://localhost:6379 |
| `DEBUG` | Debug mode | False |
| `FRONTEND_URL` | Frontend application URL | http://localhost:3000 |

### Email Configuration

The system supports various SMTP providers:

#### Gmail
```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

#### Outlook
```env
MAIL_SERVER=smtp-mail.outlook.com
MAIL_PORT=587
MAIL_USERNAME=your-email@outlook.com
MAIL_PASSWORD=your-password
```

## 🧪 Testing

### Run Tests

```bash
# Install test dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Run tests with coverage
pytest --cov=app --cov-report=html
```

### Test Structure

```
tests/
├── conftest.py              # Test configuration
├── test_auth.py             # Authentication tests
├── test_users.py            # User management tests
└── test_services.py         # Service layer tests
```

## 🚀 Deployment

### Production Environment

1. **Environment Setup**

```bash
# Production environment file
cp .env.example .env.prod

# Update with production values
DATABASE_URL=postgresql+asyncpg://prod_user:prod_pass@db_host:5432/prod_db
SECRET_KEY=super-secure-production-key
DEBUG=False
FRONTEND_URL=https://your-domain.com
```

2. **Docker Production Deployment**

```bash
# Build production image
docker build -f docker/Dockerfile -t fastapi-user-management:latest .

# Run with docker-compose
docker-compose -f docker/docker-compose.prod.yml up -d
```

3. **Manual Deployment**

```bash
# Install production dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start with Gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

### VPS Deployment

For VPS deployment, you can use the provided Docker setup or deploy manually:

1. **Server Requirements**
   - Ubuntu 20.04+ or similar
   - Python 3.11+
   - PostgreSQL 13+
   - Nginx (reverse proxy)
   - SSL certificate

2. **Nginx Configuration**

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

3. **Systemd Service**

```ini
[Unit]
Description=FastAPI User Management
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/fastapi-user-management
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 127.0.0.1:8000
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

## 📝 Database Migrations

### Create Migration

```bash
alembic revision --autogenerate -m "Description of changes"
```

### Apply Migrations

```bash
# Upgrade to latest
alembic upgrade head

# Upgrade to specific revision
alembic upgrade <revision_id>

# Downgrade
alembic downgrade -1
```

### Migration History

```bash
# Show migration history
alembic history

# Show current revision
alembic current
```

## 🔒 Security Considerations

1. **Change Default Secret Key** - Always use a strong, unique secret key in production
2. **Use HTTPS** - Deploy with SSL/TLS certificates
3. **Database Security** - Use strong database credentials and restrict access
4. **Email Security** - Use app passwords or OAuth for email authentication
5. **Rate Limiting** - Implement rate limiting for API endpoints
6. **Input Validation** - All inputs are validated using Pydantic schemas
7. **CORS Configuration** - Configure CORS for your specific domain

## 📊 Monitoring

### Health Checks

The application provides multiple health check endpoints:

- `/health` - Overall application health
- `/health/db` - Database connectivity
- `/health/ready` - Kubernetes readiness probe
- `/health/live` - Kubernetes liveness probe

### Logging

Structured logging is configured throughout the application:

```python
import logging
logger = logging.getLogger(__name__)
logger.info("User registered", extra={"user_id": user.id, "email": user.email})
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Make your changes and add tests
4. Run tests: `pytest`
5. Format code: `black app/ tests/`
6. Commit your changes: `git commit -am 'Add new feature'`
7. Push to the branch: `git push origin feature/new-feature`
8. Create a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)

## 🆘 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/your-repo/issues) page
2. Create a new issue with detailed information
3. Include error logs and configuration details

---

Built with ❤️ using FastAPI, PostgreSQL, and modern Python practices.