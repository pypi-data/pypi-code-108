import os
from traceback import format_exception

from django.conf import settings

from celery import Celery
from celery.signals import task_failure

from .util.core_helpers import get_site_preferences
from .util.email import send_email

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "aleksis.core.settings")

app = Celery("aleksis")  # noqa
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


@task_failure.connect
def task_failure_notifier(
    sender=None, task_id=None, exception=None, args=None, kwargs=None, traceback=None, **__
):
    recipient_list = [e[1] for e in settings.ADMINS]
    send_email(
        template_name="celery_failure",
        from_email=get_site_preferences()["mail__address"],
        recipient_list=recipient_list,
        context={
            "task_name": sender.name,
            "task": str(sender),
            "task_id": str(task_id),
            "exception": str(exception),
            "args": args,
            "kwargs": kwargs,
            "traceback": "".join(format_exception(type(exception), exception, traceback)),
        },
    )
