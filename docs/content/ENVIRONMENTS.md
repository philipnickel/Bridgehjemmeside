# Environment Setup & Configuration

Complete guide to setting up and configuring different environments for the Bridge Club Management System.

## 🌍 Environment Overview

| Environment | Purpose | Database | URL | Settings Module |
|-------------|---------|----------|-----|-----------------|
| **Local** | Development & Testing | SQLite | http://127.0.0.1:8000/ | `settings.local` |
| **Develop** | Feature Testing & Demo | MySQL (Test) | ruder10-dev.pythonanywhere.com | `settings.develop` |
| **Production** | Live Site | MySQL (Prod) | ruder10.pythonanywhere.com | `settings.production` |

## 💻 Local Development Environment

### Initial Setup
```bash
# Navigate to project
cd bridge_club_management

# Install dependencies
pip install -r requirements/local.txt

# Create environment file
cp .env.template .env
# Edit .env with your local settings

# Set Django settings
export DJANGO_SETTINGS_MODULE=bridge_club_management.settings.local

# Setup database
python manage.py migrate
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

### Local Configuration
**Settings File**: `bridge_club_management/settings/local.py`

**Key Features**:
- SQLite database (`db_local.sqlite3`)
- Debug mode enabled
- Console email backend (emails printed to console)
- Django Debug Toolbar (optional)
- Static files served by Django

**Environment Variables** (`.env` file):
```bash
# Django Settings
DJANGO_SECRET_KEY=your-local-secret-key-here
DEBUG=True

# Database (SQLite - no additional config needed)
# Email (optional for local)
DJANGO_EMAIL_HOST_USER=your-email@example.com
DJANGO_EMAIL_HOST_PASSWORD=your-app-password
```

### Local Database Management
```bash
# Reset local database (if needed)
rm db_local.sqlite3
python manage.py migrate
python manage.py createsuperuser

# Load test data (if fixtures exist)
python manage.py loaddata fixtures.json

# Backup local data
python manage.py dumpdata > local_backup.json
```

## 🧪 Development Server Environment

### PythonAnywhere Development Server Setup

**Settings File**: `bridge_club_management/settings/develop.py`

**Key Features**:
- MySQL test database (`Ruder10$bridgeclub_dev`)
- Debug mode enabled
- Console email backend
- Separate from production data
- Real server environment testing

### Development Server Configuration
```bash
# On PythonAnywhere dev server
export DJANGO_SETTINGS_MODULE=bridge_club_management.settings.develop

# Required environment variables:
export DJANGO_SECRET_KEY=your-dev-secret-key
export DB_PASSWORD=your-dev-database-password
export DB_NAME=Ruder10$bridgeclub_dev
export DB_USER=Ruder10
export DB_HOST=Ruder10.mysql.pythonanywhere-services.com
```

### Development Server Deployment
```bash
# SSH to PythonAnywhere
ssh Ruder10@ssh.pythonanywhere.com

# Navigate to dev directory
cd /home/Ruder10/Bridgehjemmeside-dev/bridge_club_management

# Pull latest develop branch
git pull origin develop

# Install/update dependencies
pip3.10 install --user -r requirements/production.txt

# Apply migrations
python3.10 manage.py migrate

# Collect static files
python3.10 manage.py collectstatic --noinput

# Reload web app (via PythonAnywhere dashboard)
```

## 🚀 Production Environment

### PythonAnywhere Production Server

**Settings File**: `bridge_club_management/settings/production.py`

**Key Features**:
- MySQL production database (`Ruder10$default`)
- Debug mode disabled
- SMTP email backend
- Security headers enabled
- Performance optimizations

### Production Configuration
```bash
# On PythonAnywhere production server
export DJANGO_SETTINGS_MODULE=bridge_club_management.settings.production

# Required environment variables:
export DJANGO_SECRET_KEY=your-production-secret-key
export DB_PASSWORD=your-production-database-password
export DB_NAME=Ruder10$default
export DB_USER=Ruder10
export DB_HOST=Ruder10.mysql.pythonanywhere-services.com

# Email configuration
export DJANGO_EMAIL_HOST_USER=your-email@gmail.com
export DJANGO_EMAIL_HOST_PASSWORD=your-app-password
```

### Production Security Settings
The production environment includes additional security measures:
```python
# Security headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# HTTPS settings (when SSL is enabled)
# SECURE_SSL_REDIRECT = True
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True
```

## 🔧 Settings Architecture

### Base Settings (`base.py`)
Contains shared configuration for all environments:
- Installed apps
- Middleware
- Template settings
- Static file configuration
- Internationalization settings
- CKEditor configuration

### Environment-Specific Settings
Each environment imports base settings and overrides specific values:

```python
# Example: local.py
from .base import *

SECRET_KEY = 'local-dev-key'
DEBUG = True
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db_local.sqlite3',
    }
}
```

## 📊 Database Configuration

### Local (SQLite)
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db_local.sqlite3',
    }
}
```

### Development/Production (MySQL)
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': '3306',
    }
}
```

## 📧 Email Configuration

### Local Development
```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```
Emails are printed to the console instead of being sent.

### Development Server
```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```
Same as local for testing purposes.

### Production
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = os.getenv('DJANGO_EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('DJANGO_EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = True
```

## 🗂️ Static Files Configuration

### Local Development
```python
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
```
Django serves static files directly.

### Production Servers
```python
STATIC_ROOT = '/home/Ruder10/Bridgehjemmeside/bridge_club_management/static'
```
Static files are collected and served by the web server.

## 🔄 Environment Switching

### Quick Environment Switch
```bash
# Local development
export DJANGO_SETTINGS_MODULE=bridge_club_management.settings.local
python manage.py runserver

# Development server testing
export DJANGO_SETTINGS_MODULE=bridge_club_management.settings.develop
python manage.py check

# Production testing
export DJANGO_SETTINGS_MODULE=bridge_club_management.settings.production
python manage.py check --deploy
```

### Django Settings Module Priority
Django looks for settings in this order:
1. `DJANGO_SETTINGS_MODULE` environment variable
2. `manage.py` default (set to `local`)
3. Django default (not applicable here)

## 🛡️ Security Considerations

### Environment Variables
- Never commit `.env` files to version control
- Use different secret keys for each environment
- Store production credentials securely
- Regularly rotate secret keys and passwords

### Database Security
- Separate databases for each environment
- Regular backups of production data
- Test database can be wiped/reset safely
- No production data in development environments

### Debug Mode
- Always disabled in production
- Provides detailed error pages in development
- Can expose sensitive information if enabled in production

## 🚨 Troubleshooting

### Common Issues

**ImportError: No module named 'settings'**
```bash
export DJANGO_SETTINGS_MODULE=bridge_club_management.settings.local
```

**Database connection error**
- Check environment variables are set
- Verify database credentials
- Ensure MySQL service is running (servers)

**Static files not loading**
```bash
python manage.py collectstatic --noinput
```

**Migration conflicts**
```bash
python manage.py migrate --merge
```

### Environment Validation
```bash
# Check current environment configuration
python manage.py check

# Production readiness check
python manage.py check --deploy

# View current settings
python manage.py shell
>>> from django.conf import settings
>>> print(settings.DEBUG)
>>> print(settings.DATABASES)
```

---
*For deployment-specific instructions, see [DEPLOYMENT.md](DEPLOYMENT.md)*