from celery import Celery, Task, current_app, current_task

# Added type hint for celery app
celery: Celery = current_app
# Added type hint for current task
celery_task: Task = current_task
