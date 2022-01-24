import os

SECRET_KEY = 'fake-key'
INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.postgres',
    'pfx.pfxcore',
    'tests',
]

MIDDLEWARE = [
    'pfx.pfxcore.middleware.LocaleMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
    'pfx.pfxcore.middleware.AuthenticationMiddleware',
]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

PFX_SECRET_KEY = "fake-secret-key"
PFX_TOKEN_VALIDITY = None

ROOT_URLCONF = 'tests.urls'
APPEND_SLASH = False

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
PFX_RESET_PASSWORD_URL = (
    'http://localhost:8000/test?token={token}&uidb64={uid}')
PFX_SITE_NAME = 'Assocman'

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
    }
]
