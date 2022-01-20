# Copyright 2016 to 2021, Cisco Systems, Inc., all rights reserved.

"""Baseline (incomplete) Django settings, to be completed by other modules.

Submodule is responsible to do::

    import logging.config
    from yangsuite.settings.base import *

    SECRET_KEY = ...
    DEBUG = ...
    ALLOWED_HOSTS = ...

    # make any config overrides desired

    # define any additional configs needed (e.g., for production deployment)
"""

import configparser
import traceback
import logging
import logging.config
import os
from pkg_resources import iter_entry_points, VersionConflict

from yangsuite.application import read_prefs
from yangsuite.paths import set_base_path, get_path
import yangsuite.apps

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

config = read_prefs()
prefs = config[configparser.DEFAULTSECT]

# MEDIA_ROOT contains, device profiles, user specific yang files, etc...
MEDIA_ROOT = (os.environ.get('MEDIA_ROOT') or
              prefs.get('data_path') or
              os.path.join(BASE_DIR, 'data') + os.sep)

# Application definition

INSTALLED_APPS = [
    # Let whitenoise, not django itself, manage static files
    'whitenoise.runserver_nostatic',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'yangsuite',
    'django_registration',
]

yangsuite.apps.FAILED_APPS = {}

# Auto-enable plugins that have registered under yangsuite.apps
for entry_point in iter_entry_points(group='yangsuite.apps', name=None):
    try:
        app_config = entry_point.load()
        # If the app is already in the list, don't double-add it,
        # as that will make Django unhappy.
        if app_config.name not in INSTALLED_APPS:    # noqa
            INSTALLED_APPS.append(app_config.name)    # noqa
    except Exception as exc:
        name = entry_point.dist.project_name
        if isinstance(exc, VersionConflict):
            message = exc.report()
        else:
            message = str(exc)
            logging.debug(traceback.format_exc())
        logging.error('Error in loading YANG Suite app "%s": %s',
                      name, exc)
        yangsuite.apps.FAILED_APPS[name] = message

# Disable user registration by default
REGISTRATION_OPEN = False

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # Use whitenoise to manage static files to avoid cache issues
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'yangsuite.middleware.send_to_plugins_once_if_plugin_errors',
]

ROOT_URLCONF = 'yangsuite.urls'

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
                'yangsuite.context_processors.yangsuite_menus',
            ],
        },
    },
]

WSGI_APPLICATION = 'yangsuite.wsgi.application'

# Allow uploads of up to 50 MB in size
# All IOS XR YANG models for one release ~ 12 MB
# All IOS XE YANG models for one release ~ 14 MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 52428800

# Allow up to 25 MB of data to be sent from browser to web server.
# This is needed for large custom RPCs to be processed.
DATA_UPLOAD_MAX_MEMORY_SIZE = 25600000

# After logging in, user lands at the home page (unless request has 'next=...')
LOGIN_REDIRECT_URL = "/"

# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(MEDIA_ROOT, 'db.sqlite3'),
        'OPTIONS': {
            'timeout': 180
        }
    }
}

# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

VALIDATOR_PFX = 'django.contrib.auth.password_validation'

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': VALIDATOR_PFX + '.UserAttributeSimilarityValidator',
    },
    {
        'NAME': VALIDATOR_PFX + '.MinimumLengthValidator',
    },
    {
        'NAME': VALIDATOR_PFX + '.CommonPasswordValidator',
    },
    {
        'NAME': VALIDATOR_PFX + '.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Explicitly pass MEDIA_ROOT to paths module since we're going to be
# calling paths.get_path below, before this file has been fully loaded
# into django.conf.settings
set_base_path(MEDIA_ROOT)

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS = [
]


# Don't use Django's default logging configuration - we'll do so ourselves
LOGGING_CONFIG = None

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format':
            "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
        'verbose': {
            'format':
            "[%(asctime)s.%(msecs)03d %(levelname)-7s %(name)32s :"
            "%(lineno)4d]\n%(message)s",
            'datefmt': "%Y-%m-%d %H:%M:%S",
        },
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': ("%(asctime)s.%(msecs)03d %(levelname)s "
                       "%(name)s %(lineno)d %(funcName)s %(message)s"),
            'datefmt': "%Y-%m-%d %H:%M:%S",
        },
    },
    'handlers': {
        'console': {
            'level': 'WARNING',
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
        },
        'textlog': {
            # Values used to create the handler, set its level and formatter
            '()': 'logging.handlers.RotatingFileHandler',
            'level': 'DEBUG',
            'formatter': 'verbose',
            # Values passed to the handler instance as keyword arguments
            'filename': get_path('logfile', filename='yangsuite.log'),
            'mode': 'w',   # do not truncate when (re)starting the server
            'maxBytes': (128 * 1024),
            'backupCount': 9,
            'encoding': 'utf-8',
        },
        'jsonlog': {
            # Values used to create the handler, set its level and formatter
            '()': 'logging.handlers.RotatingFileHandler',
            'level': 'DEBUG',
            'formatter': 'json',
            # Values passed to the handler instance as keyword arguments
            'filename': get_path('logfile', filename='yangsuite.log.json'),
            'mode': 'w',   # do not truncate when (re)starting the server
            'maxBytes': (128 * 1024),
            'backupCount': 9,
            'encoding': 'utf-8',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'textlog'],
            'propagate': False,
            'level': 'DEBUG',
        },
        'django.db.backends': {
            'handlers': ['console', 'textlog'],
            'level': 'ERROR',
            'propagate': False,
        },
        'yangsuite': {
            'handlers': ['console', 'textlog', 'jsonlog'],
            'level': 'DEBUG',
            'propagate': False,
        },
    }
}

logging.config.dictConfig(LOGGING)
