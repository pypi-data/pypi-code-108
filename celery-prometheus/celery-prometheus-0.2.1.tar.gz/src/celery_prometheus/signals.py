from celery.signals import worker_process_shutdown
from prometheus_client import multiprocess


@worker_process_shutdown.connect()
def prometheus_mark_celery_worker_dead(pid, exitcode, **kwargs):
    """Mark a Celery worker dead on Prometheus client side."""
    multiprocess.mark_process_dead(pid)
