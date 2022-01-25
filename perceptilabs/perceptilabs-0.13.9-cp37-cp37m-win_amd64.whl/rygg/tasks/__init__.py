from rygg.celery import app as celery_app
from rygg.settings import IS_CONTAINERIZED
from rygg.tasks.celery import get_celery_task_status, enqueue_celery, cancel_celery_task
from rygg.tasks.threaded import work_in_thread, LocalTasks, get_threaded_task_status

def get_task_status(task_id):
    if IS_CONTAINERIZED:
        return get_celery_task_status(task_id)
    else:
        return get_threaded_task_status(task_id)

def cancel_task(task_id):
    if IS_CONTAINERIZED:
        cancel_celery_task(task_id)
    else:
        LocalTasks.cancel(task_id)

def run_async(task_name, threaded_fn, *args, **kwargs):
    if IS_CONTAINERIZED:
        return enqueue_celery(task_name, *args, **kwargs)
    else:
        return work_in_thread(threaded_fn, *args, **kwargs)
