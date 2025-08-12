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
        'NAME': os.environ.get('DB_NAME', 'Ruder10$dev_test_site'),
        'USER': os.environ.get('DB_USER', 'Ruder10'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST', 'Ruder10.mysql.pythonanywhere-services.com'),
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
        },
    }
}

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = '/home/Ruder10/bridgehjemmeside-staging/bridge_club_management/static'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = '/home/Ruder10/bridgehjemmeside-staging/bridge_club_management/media'

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

# Email backend for staging (console backend for testing)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Development toolbar for staging
if DEBUG:
    try:
        import debug_toolbar
        INSTALLED_APPS += ['debug_toolbar']
        MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
        INTERNAL_IPS = ['127.0.0.1']
    except ImportError:
        pass 