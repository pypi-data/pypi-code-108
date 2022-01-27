# Copyright (c) Qotto, 2021

"""
Eventy aiohttp integration configuration
"""

__all__ = [
    'AIOHTTP_WEB_ACCESS_DISABLE_HEALTH_LOGGING',
    'AIOHTTP_WEB_ACCESS_HEALTH_ROUTE',
]

AIOHTTP_WEB_ACCESS_DISABLE_HEALTH_LOGGING: bool = True
"""
Disable aiohttp web server access logs for health checks
"""

AIOHTTP_WEB_ACCESS_HEALTH_ROUTE: str = '/health'
"""
Route for health checks
"""
