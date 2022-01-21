"""Constants used by the deployment script"""
from askbot.utils.console import bold

DEFAULT_PROJECT_NAME = 'askbot_site'
DEFAULT_MEDIA_ROOT_SUBDIR = 'upfiles'
DEFAULT_STATIC_ROOT_SUBDIR = 'static'

SQLITE = 'sqlite'
DEFAULT_SQLITE_DB_NAME = 'db.sqlite'
DATABASE_ENGINE_CHOICES = (
    ('postgresql', 'PostgreSQL'),
    (SQLITE, 'SQLite'),
    ('mysql', 'MySQL'),
    ('oracle', 'Oracle')
)
DATABASE_ENGINE_CODES = {'postgresql': 'django.db.backends.postgresql_psycopg2',
                         SQLITE: 'django.db.backends.sqlite3',
                         'mysql': 'django.db.backends.mysql',
                         'oracle': 'django.db.backends.oracle'}

ROOT_DIR_HELP = 'the ' + bold('Root') + \
        ' directory path (relative or absolute).\n' + \
        'This directory will contain the Django project\'s manage.py file'

PROJ_NAME_HELP = 'the ' + bold('Project') + \
        ' directory name.\nWill be a subdirectory within the ' + \
        bold('Root') + ' for the settings.py, urls.py files'

MEDIA_ROOT_HELP = 'value of the ' + bold('MEDIA_ROOT') + \
        ' setting for the settings.py file.\n ' + \
        'This directory is for the user uploaded files.\n ' + \
        'Default is /upfiles within the ' + bold('Root') + ' directory.'

LOG_FILE_PATH_HELP = 'Path to the log file. ' + \
        'If path is absolute - will be used as is. ' + \
        'Relative path will be appended to ${ROOT_DIR}.'

MEDIA_ROOT_HELP = 'value of the ' + bold('MEDIA_ROOT') + \
        ' setting for the settings.py file.\n ' + \
        'This directory is for the user uploaded files.\n ' + \
        'Default is /upfiles within the ' + bold('Root') + ' directory.'

DOMAIN_NAME_HELP = 'domain name of your Askbot site. Used for the ' + \
        bold('ALLOWED_DOMAINS') + ' setting.'

LANGUAGE_CODE_HELP = 'two or four letter with a dash language code (e.g. ' + \
        bold('fr') + ', ' + bold('de') + ', ' + bold('zh_CN') + '.\n ' + \
        'Value of the ' + bold('LANGUAGE_CODE') + ' setting.\n ' + \
        'Default value is ' + bold('en') + '.'

DATABASE_ENGINE_HELP = 'database engine'

USE_FORCE_PARAMETER = 're-run askbot-setup with a --force parameter'
