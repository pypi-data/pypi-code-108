'''
    Shared django settings for between projects.

    Copyright 2009-2022 DeNova
    Last modified: 2022-01-10

    This file is open source, licensed under GPLv3 <http://www.gnu.org/licenses/>.
'''

try:
    # only importing to verify django's installed
    import django
except ModuleNotFoundError:
    import sys
    sys.exit('Django required')

import os
from tempfile import gettempdir

from denova.os.user import whoami

DJANGO_ADDONS_PROJECT_PATH = os.path.dirname(__file__).replace('\\','/')

# probably want to include this directory in the TEMPLATES_DIR so the shared admin templates are used
DJANGO_ADDONS_TEMPLATE_DIR = os.path.join(DJANGO_ADDONS_PROJECT_PATH, 'templates')
DJANGO_ADDONS_STATIC_DIR = os.path.join(DJANGO_ADDONS_PROJECT_PATH, 'static')

APPEND_SLASH = True

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Atlantic/Reykjavik'

# If you set this to True, Django will use timezone-aware datetimes.
# Our CRM requires this to be set True; adjust in app's settings if you want to override.
USE_TZ = True

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-CA'
LANGUAGES = [
    ('en', 'English'),
    ('en-CA', 'English-Canadian'),
]

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

USE_L10N = True

# reduce "database is locked" errors, especially with sqlite
DATABASE_OPTIONS = {'timeout': 30}

# django staticfiles app url prefix for static files
STATIC_URL = "/static/"

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

# login urls
LOGIN_REDIRECT_URL = '/'

# do not allow any pages from our site to be wrapped in frames
X_FRAME_OPTIONS = 'DENY'

INSTALLED_APPS = [
    'django.contrib.humanize',
    'django.contrib.staticfiles',

    # https://pypi.python.org/pypi/django-bootstrap4
    'bootstrap4',
     # https://pypi.python.org/pypi/django-forms-bootstrap/
    'django_forms_bootstrap',

    'django.contrib.admin',
    'django.contrib.auth',
]

# List of template loaders that know how to import templates from various sources.
TEMPLATE_LOADERS = [
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader'
]

# List of processors
TEMPLATE_CONTEXT_PROCESSORS = [
    'django.template.context_processors.debug',
    'django.template.context_processors.request',
    'django.contrib.auth.context_processors.auth',
    'django.contrib.messages.context_processors.messages',

    'denova.django_addons.context_processors.custom',
]

# order recommended by django 2.0 docs
MIDDLEWARE = [
    #'django.middleware.cache.UpdateCacheMiddleware',    # This must be first on the list to use caching
    # log debug info before a middleware processor short-circuits later middleware
    'denova.django_addons.middleware.debug.DebugMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    #'django.middleware.common.BrokenLinkEmailsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'denova.django_addons.middleware.template.RequestMiddleware',
    'denova.django_addons.middleware.template.SettingsMiddleware',
    #'denova.django_addons.middleware.debug.StripCodeComments',

    #'django.middleware.cache.FetchFromCacheMiddleware', # This must be last to use caching
]


# Log everything to a file. Log errors, such as HTTP 500 error when DEBUG=False, to email.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
DJANGO_USER = whoami()
DJANGO_LOG_DIR = f'/var/local/log/{DJANGO_USER}'
DJANGO_LOG_FILENAME = f'{DJANGO_LOG_DIR}/django.log'
try:
    if not os.path.exists(DJANGO_LOG_DIR):
        os.makedirs(DJANGO_LOG_DIR)
except Exception:
    try:
        # each log needs a unique name per user or there are permission conflicts
        DJANGO_LOG_FILENAME = os.path.join(gettempdir(), f'django_{DJANGO_USER}.log')
    except Exception:
        from tempfile import NamedTemporaryFile
        DJANGO_LOG_FILENAME = NamedTemporaryFile(mode='a', prefix='django', dir=gettempdir())

LOGGING_CONFIG = None
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'formatters': {
        'verbose': {
            'format': '%(asctime)s %(levelname)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '[%(asctime)s %(module)s] %(levelname)s: %(message)s'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
            'formatter': 'verbose'
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'formatter': 'verbose',
            'filename': DJANGO_LOG_FILENAME,
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['file', 'mail_admins'],
            'level': 'INFO',
            'propagate': True,
        },
    }
}
