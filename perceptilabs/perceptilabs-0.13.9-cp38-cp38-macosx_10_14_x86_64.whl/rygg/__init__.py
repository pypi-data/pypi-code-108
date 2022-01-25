from __future__ import absolute_import, unicode_literals
__version__='0.13.9'

from .celery import app as celery_app
__all__ = ("celery_app",)