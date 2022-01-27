# Copyright (c) Qotto, 2021

"""
Provides logging handlers to integrate tracing in log messages.

Include a :class:`simple_handler.SimpleHandler`
and a Google Kubernetes Engines specific :class:`gke_handler.GkeHandler`
"""

from .gke_handler import GkeHandler
from .info_providers import correlation_id_provider, request_id_provider
from .simple_handler import SimpleHandler

__all__ = [
    'correlation_id_provider',
    'request_id_provider',
    'SimpleHandler',
    'GkeHandler',
]
