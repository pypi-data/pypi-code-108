from django.core.management.base import BaseCommand

from security.backends.writer import set_stale_celery_task_log_state


class Command(BaseCommand):

    def handle(self, **options):
        set_stale_celery_task_log_state()
