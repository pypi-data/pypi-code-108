def produce_app(task_name:str):
    from authc import authc
    from celery import Celery
    auth = authc()
    broker = auth['celery_broker']
    backend = auth['celery_backend']
    app = Celery(task_name, broker=broker, backend=backend)
    app.conf.update( CELERY_REDIS_MAX_CONNECTIONS = 100,)
    return app
