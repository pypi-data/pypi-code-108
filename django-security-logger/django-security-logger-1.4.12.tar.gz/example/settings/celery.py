import os
import sys

from django.conf import settings

from django_celery_extensions.celery import Celery


app = Celery('example', task_cls='security.task:LoggedTask')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks()
