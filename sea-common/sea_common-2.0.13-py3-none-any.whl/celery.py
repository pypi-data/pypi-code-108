from celery import current_app

from .config import settings


def create_celery():
    celery_app = current_app
    celery_app.config_from_object(settings)

    return celery_app
