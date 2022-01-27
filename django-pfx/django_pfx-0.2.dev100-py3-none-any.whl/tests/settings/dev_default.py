from .common import *  # noqa

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'test-pfx',
        'USER': 'django',
        'PASSWORD': 'django',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
