# Copyright (c) Qotto, 2021

"""
Eventy django integration configuration
"""

__all__ = [
    'DJANGO_ACCESS_DISABLE_HEALTH_LOGGING',
    'DJANGO_ACCESS_HEALTH_ROUTE',
]

DJANGO_ACCESS_DISABLE_HEALTH_LOGGING: bool = True
"""
Disable django access logs for health route
"""

DJANGO_ACCESS_HEALTH_ROUTE: str = '/health'
"""
Route for health checks
"""
