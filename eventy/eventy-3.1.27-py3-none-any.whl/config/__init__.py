# Copyright (c) Qotto, 2021

"""
Eventy configuration
"""

__all__ = [
    'SERVICE_NAME',
]

SERVICE_NAME: str = '-'
"""
Do not update with:
>>> from eventy.config import SERVICE_NAME
>>> SERVICE_NAME = 'my_service'

If you want to update the value you need to do:
>>> from eventy import config
>>> config.SERVICE_NAME = 'my_service'
"""
