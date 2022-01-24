from authc import authc
from celery import Celery


def produce_cn_app(task_name: str):
    auth = authc()
    broker = auth['cn_celery_broker']
    backend = auth['cn_celery_backend']
    app = Celery(task_name, broker=broker, backend=backend)
    app.conf.update(CELERY_REDIS_MAX_CONNECTIONS=100,)
    return app
