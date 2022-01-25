"""
views_schema
============

The classes in this module define the (json) schema which services and tools
use to communicate.

Having these classes in one place makes it possible to share schema definitions
across services, so that services may speak the same "language".
"""

from .queryset_manager import *
from .partitioning import *
from .docs import *
from .base_data_retriever import *
from .generic import *
