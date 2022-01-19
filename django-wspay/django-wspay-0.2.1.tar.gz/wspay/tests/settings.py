DEBUG = True
USE_TZ = True
TIME_ZONE = "UTC"
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "HOST": "127.0.0.1",
        "NAME": "wspay",
        "USER": ""
    }
}
MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]
ROOT_URLCONF = "wspay.tests.urls"
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "wspay",
]
SITE_ID = 1
TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "APP_DIRS": True,
    "OPTIONS": {
        "debug": True,
        "context_processors": [
            "django.contrib.auth.context_processors.auth",
            "django.template.context_processors.debug",
            "django.template.context_processors.i18n",
            "django.template.context_processors.media",
            "django.template.context_processors.static",
            "django.template.context_processors.tz",
            "django.template.context_processors.request",
        ],
    },
}]
SECRET_KEY = "ws-pay-secret-key"


def _shop_id():
    return 'MojShop'


WS_PAY_SHOP_ID = _shop_id
WS_PAY_SECRET_KEY = 'wspay.tests.utils.secret_key'
WS_PAY_DEVELOPMENT = True
