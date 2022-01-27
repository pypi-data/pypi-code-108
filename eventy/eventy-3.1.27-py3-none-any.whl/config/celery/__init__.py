# Copyright (c) Qotto, 2021

"""
Eventy celery integration configuration
"""

__all__ = [
    'CELERY_AUTO_FORGET_ON_GET',
]

CELERY_AUTO_FORGET_ON_GET: bool = False
"""
Use custom AsyncResult class to automatically forget tasks after get()
"""
