# Copyright (c) Qotto, 2021

"""
Eventy sanic integration configuration
"""

__all__ = [
    'SANIC_ACCESS_DISABLE_HEALTH_LOGGING',
    'SANIC_ACCESS_HEALTH_ROUTE',
]

SANIC_ACCESS_DISABLE_HEALTH_LOGGING: bool = True
"""
Disable sanic access logs for health checks
"""

SANIC_ACCESS_HEALTH_ROUTE: str = '/health'
"""
Route for health checks
"""
