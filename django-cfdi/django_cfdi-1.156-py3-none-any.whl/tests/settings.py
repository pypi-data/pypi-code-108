import os

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

SECRET_KEY = "fake-key"

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'cfdi',
]
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.template.context_processors.debug",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "workflow.context_processors.custom_context",
            ]
        },
    }
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'tests_cfdi',
    }
}



CFDI_ERROR_CALLBACK = "tests.cfdi_callbacks.error_callback"
CFDI_POST_TIMBRADO_CALLBACK = "tests.cfdi_callbacks.post_timbrado_callback"

CFDI_DFACTURE_AUTH = {
    "dev": {"usuario": "", "password": ""},
    "prod": {"usuario": "", "password": ""},
}
TEST_NO_CERTIFICADO = "30001000000300023701"
TEST_RFC = "AAA010101AAA"
TEST_RAZON_SOCIAL = "TRANSPORTES SA DE CV"
TEST_REGIMEN_FISCAL = "601"
TEST_CERTIFICADO = "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"
TEST_PEM = None

if os.path.exists("{}/local_settings.py".format(os.path.dirname(__file__))):
    from .local_settings import *