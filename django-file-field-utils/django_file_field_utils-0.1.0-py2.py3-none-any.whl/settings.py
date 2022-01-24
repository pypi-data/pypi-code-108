import os

from django.conf import settings

PROJECT_PATH_DEFAULT, _ = os.path.split(os.path.split(os.path.realpath(__file__))[0])
PROJECT_PATH = getattr(settings, "PROJECT_PATH", PROJECT_PATH_DEFAULT)

PRIVATE_ROOT_DEFAULT = os.path.join(PROJECT_PATH, "privatemedia")
PRIVATE_ROOT = getattr(settings, "PRIVATE_ROOT", PRIVATE_ROOT_DEFAULT)

PRIVATE_URL_DEFAULT = "/privatemedia/"
PRIVATE_URL = getattr(settings, "PRIVATE_URL", PRIVATE_URL_DEFAULT)
