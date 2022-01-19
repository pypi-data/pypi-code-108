"""
Django settings for demo project.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""
import os
from django.contrib.messages import constants as messages

# -------------------------------------------------------------------------
# Application Metadata
# -------------------------------------------------------------------------
# The current version of the DEMO application
APP_VERSION = '0.1.3'

# App identifiers
APP_CODE = 'DEMO'.upper()   # Used for database lookups
APP_NAME = 'The Demo Site'  # Displayed in some generic UI scenarios
SUB_APPS = {
    'EMERGENCY': 'Emergency Management Demo',
    'DIPLOMA': 'Diploma Order Demo',
    'ARRANGEMENT': 'By-Arrangement Demo',
}

# On-premises apps will have additional "context" appended to the URL
#   i.e. https://app.banner.pdx.edu/demo/index
# AWS apps will not have this (set to None)
URL_CONTEXT = None  # 'demo'

# When no local_settings.py file exists, assume running in AWS
is_aws = not os.path.isfile('demo/local_settings.py')

# I needed this in APC, but it caused issues in the demo site.
# APPEND_SLASH = False

# -------------------------------------------------------------------------
# -------------------------------------------------------------------------

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# For local development, Finti responses can be stored in SQLite for simulated Finti calls
# Override these in local_settings.py
FINTI_SAVE_RESPONSES = False            # Save/record actual Finti responses for offline use?
FINTI_SIMULATE_CALLS = False            # Simulate Finti calls. 404 if response not previously saved.
FINTI_SIMULATE_WHEN_POSSIBLE = False    # Simulate Finti calls only when cached response exists.

# SECURITY WARNING: Overwrite this key in local_settings.py for production!
SECRET_KEY = 'somesecretkey123'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = []

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # PSU Base Plugin:
    'django_cas_ng',
    'crequest',
    'psu_base',
    'sass_processor',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'demo.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['demo/templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'psu_base.context_processors.auth',
                'psu_base.context_processors.util'
            ],
            'libraries':{
                # If demo had a taglib, it would need to be defined here:
                # 'demo_taglib': 'demo.templatetags.demo_taglib',
            }
        },
    },
]

WSGI_APPLICATION = 'demo.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases
if is_aws:
    # AWS Database
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('RDS_DB_NAME', 'eb'),
            'USER': os.environ.get('RDS_USERNAME'),
            'PASSWORD': os.environ.get('RDS_PASSWORD'),
            'HOST': os.environ.get('RDS_HOSTNAME'),
            'PORT': os.environ.get('RDS_PORT'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        },
    }

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# For caching things (like database results)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}

# SESSION_ENGINE = "django.contrib.sessions.backends.cache"

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators
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
# https://docs.djangoproject.com/en/2.2/topics/i18n/
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/Vancouver'
USE_I18N = True
USE_L10N = True
USE_TZ = False

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# SASS (https://github.com/jrief/django-sass-processor)
SASS_PROCESSOR_ROOT = os.path.join(BASE_DIR, 'sass_build')
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'sass_processor.finders.CssFinder',
]

SASS_PROCESSOR_INCLUDE_DIRS = [
    os.path.join('demo', 'static', 'css'),
]
SASS_PROCESSOR_AUTO_INCLUDE = True  # App specific static folders are added to the libsass include dirs
SASS_PROCESSOR_INCLUDE_FILE_PATTERN = r'^.+\.scss$'
SASS_PRECISION = 8

SASS_PROCESSOR_CUSTOM_FUNCTIONS = {
    'get-color': 'psu_base.services.template_service.get_sass_color',
    'get-string': 'psu_base.services.template_service.get_sass_string',
}

# #########################################################################
# PSU Base Plugin Settings
# #########################################################################

# PSU Centralized Repository
CENTRALIZED_NONPROD = 'https://content.oit.pdx.edu/nonprod'
CENTRALIZED_PROD = 'https://content.oit.pdx.edu'

# Message classes
MESSAGE_TAGS = {
    messages.DEBUG: 'alert-info',
    messages.INFO: 'alert-info',
    messages.SUCCESS: 'alert-success',
    messages.WARNING: 'alert-warning',
    messages.ERROR: 'alert-danger',
}
FLASH_MESSAGE_POSITION = 'ANIMATE'   # TOP, BOTTOM, ANIMATE

if (not is_aws) and (not os.path.isdir('logs')):
    os.mkdir('logs')

# Logging Settings
if is_aws:
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': True,
        'formatters': {
            'standard': {
                'format': "[%(asctime)s] %(levelname)s %(message)s",
                'datefmt': "%d/%b/%Y %H:%M:%S"
            },
        },
        'handlers': {
            'null': {
                'level': 'DEBUG',
                'class': 'logging.NullHandler',
            },
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'standard'
            },
        },
        'loggers': {
            'django': {
                'handlers': ['console'],
                'propagate': True,
                'level': 'WARN',
            },
            'django.db.backends': {
                'handlers': ['console'],
                'level': 'ERROR',
                'propagate': False,
            },
            'psu': {
                'handlers': ['console'],
                'level': 'DEBUG',
            },
        }
    }
else:
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': True,
        'formatters': {
            'standard': {
                'format': "[%(asctime)s] %(levelname)s %(message)s",
                'datefmt': "%d/%b/%Y %H:%M:%S"
            },
        },
        'handlers': {
            'null': {
                'level': 'DEBUG',
                'class': 'logging.NullHandler',
            },
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'standard'
            },
            'file': {
                'level': 'DEBUG',
                'class': 'logging.FileHandler',
                'filename': 'logs/demo.log',
                'formatter': 'standard'
            },
        },
        'loggers': {
            'django': {
                'handlers': ['console', 'file'],
                'propagate': True,
                'level': 'WARN',
            },
            'django.db.backends': {
                'handlers': ['console', 'file'],
                'level': 'ERROR',
                'propagate': False,
            },
            'psu': {
                'handlers': ['console', 'file'],
                'level': 'DEBUG',
            },
        }
    }

# SSO SETTINGS
CAS_APPLY_ATTRIBUTES_TO_USER = True
CAS_CREATE_USER = True
CAS_IGNORE_REFERER = True
CAS_LOGIN_MSG = None
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'django_cas_ng.backends.CASBackend',
)
USE_PREFERRED_NAMES = True

# EMAIL SETTINGS
EMAIL_SENDER = 'noreply@pdx.edu'
EMAIL_HOST = 'mailhost.pdx.edu'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = None      # Add to local_settings.py
EMAIL_HOST_PASSWORD = None  # Add to local_settings.py

# Session expiration
SESSION_COOKIE_AGE = 30 * 60  # 30 minutes

# Globally require authentication by default
REQUIRE_LOGIN = True

# List of URLs in your app that should be excluded from global authentication requirement
# By default, the root (landing page) is public
APP_PUBLIC_URLS = ['^/$']
# If deployed on-prem, root URL will contain additional context:
if URL_CONTEXT:
    APP_PUBLIC_URLS.append(f'^/{URL_CONTEXT}/?$')

# Some PSU Base paths must be public:
PSU_PUBLIC_URLS = ['.*/psu/test', '.*/accounts/login']

# CAS will return users to the root of the application
CAS_REDIRECT_URL = f'/{URL_CONTEXT if URL_CONTEXT else ""}'
LOGIN_URL = 'cas:login'

# May be overwritten in local_settings (i.e. to use sso.stage):
CAS_SERVER_URL = 'https://sso.oit.pdx.edu/idp/profile/cas/login'

# Get SASS Variables
if os.path.isfile('demo/sass_variables.py'):
    from .sass_variables import *

# In AWS (Elastic Beanstalk), values will be in environment variables
if is_aws:
    HOST_NAME = os.environ.get('HOST_NAME', 'localhost')
    HOST_IP = os.environ.get('HOST_IP')
    HOST_URL = os.environ.get('HOST_URL')

    # This forces the CAS redirect to use SSL. Required when deployed in AWS.
    CAS_ROOT_PROXIED_AS = 'https://' + HOST_URL

    # Do not attempt to compile SASS in AWS (permission errors)
    SASS_PROCESSOR_ENABLED = False

    # https://docs.djangoproject.com/en/2.2/topics/security/#ssl-https
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

    ALLOWED_HOSTS = ['*', 'localhost', HOST_NAME, HOST_IP, HOST_URL]
    ENVIRONMENT = os.environ.get('ENVIRONMENT', 'DEV')
    CAS_SERVER_URL = os.environ.get('CAS_SERVER_URL', 'https://sso-stage.oit.pdx.edu/idp/profile/cas/login')
    DEBUG = str(os.environ.get('DEBUG', 'False')).lower() == 'true'
    SECRET_KEY = os.environ.get('SECRET_KEY', None)
    FINTI_URL = os.environ.get('FINTI_URL', 'https://ws-test.oit.pdx.edu')
    FINTI_TOKEN = os.environ.get('FINTI_TOKEN', None)

    # Email Settings
    EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', None)
    EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', None)

# Otherwise, override settings with values from local_settings.py
else:
    from .local_settings import *
