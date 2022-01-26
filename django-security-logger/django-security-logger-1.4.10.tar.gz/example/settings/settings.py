from settings.base import *  # pylint: disable=E0401


DEBUG = TEMPLATE_DEBUG = THUMBNAIL_DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(PROJECT_DIR, 'var', 'db', 'sqlite.db'),
        'USER': '',
        'PASSWORD': '',
    },
    'security': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(PROJECT_DIR, 'var', 'db', 'log.db'),
        'USER': '',
        'PASSWORD': '',
    },
}

ROOT_URLCONF = 'urls'

STATIC_ROOT = ''

# Additional locations of static files
STATICFILES_DIRS = (
    STATICFILES_ROOT,
)

SECURITY_LOG_DB_NAME = 'security'
DATABASE_ROUTERS = ['security.backends.sql.db_router.MultipleDBSecurityLoggerRouter']

ALLOWED_HOSTS = ['*']

SECURITY_BACKENDS = ['sql']
