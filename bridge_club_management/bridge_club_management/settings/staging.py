"""
Staging settings for the dev/test-site branch on PythonAnywhere
"""
from .base import *
import os

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')

# Debug can be True for staging to help with testing
DEBUG = True

ALLOWED_HOSTS = [
    'bridgeclub-dev.pythonanywhere.com',  # Replace with your dev domain
    '.pythonanywhere.com',
    'localhost',
    '127.0.0.1',
]

# Database for staging (MySQL on PythonAnywhere)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
        },
    }
}

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.environ.get('STATIC_ROOT', '/home/Ruder10/DevSite/Bridgehjemmeside/bridge_club_management/static')

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.environ.get('MEDIA_ROOT', '/home/Ruder10/DevSite/Bridgehjemmeside/bridge_club_management/media')

# Less strict security for staging
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Logging for staging (simplified - console only)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'club_management': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

# Email defaults for staging (safe by default)
TEST_SITE = True
EMAIL_SUBJECT_PREFIX = '[TEST-SITE] '
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'Bridge Klub Testsite <no-reply@test.substitutliste.dk>')
SERVER_EMAIL = os.environ.get('SERVER_EMAIL', DEFAULT_FROM_EMAIL)

# Allow enabling real email sending via environment variables
# Default to console backend for safety
EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
ENABLE_EMAILS = os.environ.get('ENABLE_EMAILS', '').lower() == 'true'

if ENABLE_EMAILS or EMAIL_BACKEND.endswith('smtp.EmailBackend'):
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
    EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
    # Accept both EMAIL_HOST_USER and DJANGO_EMAIL_HOST_USER
    EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER') or os.environ.get('DJANGO_EMAIL_HOST_USER', '')
    EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD') or os.environ.get('DJANGO_EMAIL_HOST_PASSWORD', '')
    EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'true').lower() == 'true'

# Development toolbar for staging
if DEBUG:
    try:
        import debug_toolbar
        INSTALLED_APPS += ['debug_toolbar']
        MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
        INTERNAL_IPS = ['127.0.0.1']
    except ImportError:
        pass 