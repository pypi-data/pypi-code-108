# flake8: noqa
import os

from django.contrib import messages

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
]


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.dirname(PROJECT_DIR)

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.locale.LocaleMiddleware",
]


LOCALE_PATHS = (os.path.join(BASE_DIR, "locale/"),)


def ugettext(s):
    return s


LANGUAGES = (
    ("en", ugettext("English")),
    ("de", ugettext("German")),
    ("es", ugettext("Spanish")),
)

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(PROJECT_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
            ],
        },
    },
]

WSGI_APPLICATION = "test_server.wsgi.application"

# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]

# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = "/static/"
STATICFILES_DIRS = [
    os.path.join(PROJECT_DIR, "static"),
]
STATIC_ROOT = os.path.join(BASE_DIR, "static")

MESSAGE_TAGS = {messages.ERROR: "danger"}

# CACHES = {
#     "default": {
#         "BACKEND": "redis_cache.RedisCache",
#         "LOCATION": "localhost:6379",
#         "OPTIONS": {
#             "DB": 1,
#         },
#     }
# }

DEBUG = True
ALLOWED_HOSTS = ["*"]
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": str(os.path.join(BASE_DIR, "databaase.db")),
    },
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            "datefmt": "%d/%b/%Y %H:%M:%S",
        },
        "simple": {"format": "%(levelname)s %(message)s"},
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
}

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

ROOT_URLCONF = "test_server.urls"
WSGI_APPLICATION = "test_server.wsgi.application"
SECRET_KEY = "BWdSupbQc2CiBi77NdvFYzg8VSZC4LEye4u9qnU4Bt7qD34YnKJU9XqlMqc4"

SITE_NAME = "test_server"

DEBUG = True

REGISTRATION_VERIFY_EMAIL = False
EMAIL_HOST = ""
EMAIL_PORT = 587
EMAIL_HOST_USER = ""
EMAIL_HOST_PASSWORD = ""
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = ""


AUTHLIB_OAUTH_CLIENTS = {
    "influence": {
        "client_id": os.environ.get("INFLUENCE_CLIENT_ID", ""),
        "client_secret": os.environ.get("INFLUENCE_CLIENT_SECRET", ""),
        "access_token_url": "https://api.influenceth.io/v1/auth/token",
        "authorize_url": "https://api.influenceth.io/v1/auth/authorize",
        "client_kwargs": {},
        "token_endpoint_auth_method": "client_secret_post",
    }
}
