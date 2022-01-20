"""Masterful GUI WSGI application module.

Provides access to the WSGI app object that should be executed. The WSGI
application object is implemented in Django, this module passes that object
as is to the program.

Note: The settings module environment variable must be configured prior to
creating the WSGI app object.

For more info on Django's WSGI application object, see:
https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/#the-application-object
"""
import os
import tempfile

from django.core.wsgi import get_wsgi_application
from django.core import management

# The name of the Django settings module.
_DJANGO_SETTINGS_MODULE_NAME = 'DJANGO_SETTINGS_MODULE'

# The relative path to the settings module. This is tied closely to Django
# environment setup, if project structure is changed this must be changed as
# well.
_DJANGO_SETTINGS_MODULE_PATH = 'masterful_gui.backend.settings'


def init_settings_env_variable():
  """Initializes the settings module variable in the environment.
  
  Must be called before creating the WSGI app or it'll fail.
  """
  os.environ.setdefault(_DJANGO_SETTINGS_MODULE_NAME,
                        _DJANGO_SETTINGS_MODULE_PATH)


def make_migrations():
  """Checks for model updates to create the necessary SQL updates."""
  # TODO(ray): Replace this tempfile stratefy with an official logging solution.
  # This is a placeholder technique to intercept the output of some django
  # commands before stdout to reduce the noise of the running server.
  tmp_log_file = tempfile.mkstemp()[1]
  with open(tmp_log_file, 'w') as tf:
    management.call_command('makemigrations', stdout=tf)


def migrate():
  """Applies pending SQL statements by 'makemigrations' in the database."""
  # TODO(ray): Replace this tempfile stratefy with an official logging solution.
  # This is a placeholder technique to intercept the output of some django
  # commands before stdout to reduce the noise of the running server.
  tmp_log_file = tempfile.mkstemp()[1]
  with open(tmp_log_file, 'w') as tf:
    management.call_command('migrate', stdout=tf)


def create_wsgi_app():
  """Creates a Masterful GUI WSGI app instance.
  
  As mentioned in the module docstring this only calls the Django API to obtain
  the predefined WSGI app object. You must call `init_settings_env_variable`
  before calling this function.
  
  Returns:
    The WSGI app instance..
  """
  return get_wsgi_application()