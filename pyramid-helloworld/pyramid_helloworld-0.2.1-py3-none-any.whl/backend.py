try:
    from celery import Celery
    app = Celery()
except ImportError:
    app = None
