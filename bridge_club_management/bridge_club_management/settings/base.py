"""
Base Django settings for bridge_club_management project.
These settings are common across all environments.
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'club_management.apps.ClubManagementConfig',
    'django_ckeditor_5',
    'bootstrap_datepicker_plus',
]

# Wagtail (admin + content tooling)
# Optionally enable Wagtail if installed
try:
    import wagtail  # noqa: F401
    _WAGTAIL_AVAILABLE = True
except Exception:
    _WAGTAIL_AVAILABLE = False

try:
    from wagtail.contrib import modeladmin as _wa_modeladmin  # noqa: F401
    _WAGTAIL_MODELADMIN_AVAILABLE = True
except Exception:
    _WAGTAIL_MODELADMIN_AVAILABLE = False

if _WAGTAIL_AVAILABLE:
    INSTALLED_APPS += [
        'wagtail.contrib.forms',
        'wagtail.contrib.redirects',
        'wagtail.contrib.settings',
        'wagtail.embeds',
        'wagtail.sites',
        'wagtail.users',
        'wagtail.snippets',
        'wagtail.documents',
        'wagtail.images',
        'wagtail.search',
        'wagtail.admin',
        'wagtail',
        'modelcluster',
        'taggit',
    ]
    if _WAGTAIL_MODELADMIN_AVAILABLE:
        INSTALLED_APPS += ['wagtail.contrib.modeladmin']

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Enable Wagtail redirects middleware (safe to have even if not used yet)
if _WAGTAIL_AVAILABLE:
    MIDDLEWARE += [
        'wagtail.contrib.redirects.middleware.RedirectMiddleware',
    ]

ROOT_URLCONF = 'bridge_club_management.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # Expose Wagtail settings in templates as `settings`
                'wagtail.contrib.settings.context_processors.settings',
            ],
        },
    },
]

WSGI_APPLICATION = 'bridge_club_management.wsgi.application'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'da'
TIME_ZONE = 'Europe/Copenhagen'
USE_I18N = True
USE_TZ = True

LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale'),
]

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Wagtail site branding (only used if Wagtail installed)
WAGTAIL_SITE_NAME = 'Bridge Club Management'
WAGTAILADMIN_BASE_URL = os.environ.get('WAGTAILADMIN_BASE_URL', 'http://127.0.0.1:8010')

# Choose which admin is mounted at /admin ("django" or "wagtail").
# If Wagtail is not installed, this will fall back to Django.
ADMIN_UI = os.environ.get('ADMIN_UI', 'django')

# Cron classes
CRON_CLASSES = [
    'club_management.management.commands.update_substitution_lists.Command',
]

# Custom color palette for CKEditor
customColorPalette = [
    {'color': 'hsl(4, 90%, 58%)', 'label': 'Red'},
    {'color': 'hsl(340, 82%, 52%)', 'label': 'Pink'},
    {'color': 'hsl(291, 64%, 42%)', 'label': 'Purple'},
    {'color': 'hsl(262, 52%, 47%)', 'label': 'Deep Purple'},
    {'color': 'hsl(231, 48%, 48%)', 'label': 'Indigo'},
    {'color': 'hsl(207, 90%, 54%)', 'label': 'Blue'},
    {'color': 'hsl(199, 98%, 48%)', 'label': 'Light Blue'},
    {'color': 'hsl(187, 100%, 42%)', 'label': 'Cyan'},
    {'color': 'hsl(174, 100%, 29%)', 'label': 'Teal'},
    {'color': 'hsl(122, 39%, 49%)', 'label': 'Green'},
    {'color': 'hsl(88, 50%, 53%)', 'label': 'Light Green'},
    {'color': 'hsl(66, 70%, 54%)', 'label': 'Lime'},
    {'color': 'hsl(49, 98%, 60%)', 'label': 'Yellow'},
    {'color': 'hsl(45, 100%, 51%)', 'label': 'Amber'},
    {'color': 'hsl(36, 100%, 50%)', 'label': 'Orange'},
    {'color': 'hsl(14, 91%, 54%)', 'label': 'Deep Orange'},
    {'color': 'hsl(15, 25%, 34%)', 'label': 'Brown'},
    {'color': 'hsl(0, 0%, 62%)', 'label': 'Grey'},
    {'color': 'hsl(200, 18%, 46%)', 'label': 'Blue Grey'},
    {'color': 'hsl(200, 18%, 100%)', 'label': 'White'}
]

# CKEditor 5 settings
CKEDITOR_5_CONFIGS = {
    'default': {
        'toolbar': ['heading', '|', 'bold', 'italic', 'link',
                    'bulletedList', 'numberedList', 'blockQuote', 'imageUpload', ],
    },
    'extends': {
        'blockToolbar': [
            'paragraph', 'heading1', 'heading2', 'heading3',
            '|',
            'bulletedList', 'numberedList',
            '|',
            'blockQuote',
        ],
        'toolbar': [
            'heading',
            '|',
            'bold', 'italic', 'strikethrough', 'underline', 'code', 'subscript', 'superscript', 'removeFormat',
            '|',
            'bulletedList', 'numberedList', 'todoList',
            '|',
            'outdent', 'indent',
            '|',
            'undo', 'redo',
            '-',
            'fontSize', 'fontFamily', 'fontColor', 'fontBackgroundColor', 'highlight',
            '|',
            'alignment',
            '|',
            'link', 'insertImage', 'blockQuote', 'insertTable', 'mediaEmbed',
            'codeBlock',
            '|',
            'horizontalLine', 'pageBreak',
            '|',
            'textPartLanguage',
            '|',
            'sourceEditing'
        ],
        'image': {
            'toolbar': [
                'imageTextAlternative', 'imageStyle:inline', 'imageStyle:block', 'imageStyle:side',
                '|',
                'toggleImageCaption', 'imageTextAlternative'
            ]
        },
        'table': {
            'contentToolbar': [
                'tableColumn', 'tableRow', 'mergeTableCells',
                'tableProperties', 'tableCellProperties'
            ],
            'tableProperties': {
                'borderColors': customColorPalette,
                'backgroundColors': customColorPalette
            },
            'tableCellProperties': {
                'borderColors': customColorPalette,
                'backgroundColors': customColorPalette
            }
        },
        'heading' : {
            'options': [
                { 'model': 'paragraph', 'title': 'Paragraph', 'class': 'ck-heading_paragraph' },
                { 'model': 'heading1', 'view': 'h1', 'title': 'Heading 1', 'class': 'ck-heading_heading1' },
                { 'model': 'heading2', 'view': 'h2', 'title': 'Heading 2', 'class': 'ck-heading_heading2' },
                { 'model': 'heading3', 'view': 'h3', 'title': 'Heading 3', 'class': 'ck-heading_heading3' }
            ]
        },
        'fontSize': {
            'options': [ 10, 12, 14, 'default', 18, 20, 22 ],
            'supportAllValues': True
        },
        'fontFamily': {
            'options': [
                'default',
                'Arial, Helvetica, sans-serif',
                'Courier New, Courier, monospace',
                'Georgia, serif',
                'Lucida Sans Unicode, Lucida Grande, sans-serif',
                'Tahoma, Geneva, sans-serif',
                'Times New Roman, Times, serif',
                'Trebuchet MS, Helvetica, sans-serif',
                'Verdana, Geneva, sans-serif'
            ],
            'supportAllValues': True
        },
        'fontColor': {
            'columns': 5,
            'documentColors': 10,
        },
        'fontBackgroundColor': {
            'columns': 5,
            'documentColors': 10,
        },
    }
}

# CKEditor 5 upload configurations
CKEDITOR_5_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
CKEDITOR_5_UPLOAD_PATH = "uploads/" 
