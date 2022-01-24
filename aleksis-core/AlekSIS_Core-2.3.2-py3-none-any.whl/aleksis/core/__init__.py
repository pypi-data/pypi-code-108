from importlib import metadata

from .celery import app as celery_app  # noqa

try:
    __version__ = metadata.distribution("AlekSIS-Core").version
except Exception:
    __version__ = "unknown"

default_app_config = "aleksis.core.apps.CoreConfig"
