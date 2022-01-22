import os
from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DJANGO_PROJECT.settings')

app = Celery('DJANGO_PROJECT')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.conf.task_default_queue = os.path.basename(os.path.normpath(settings.BASE_DIR))
app.autodiscover_tasks()