# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
# Copyright (C) 2021 TU Wien.
#
# Invenio-Requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Services module."""

from .components import RequestNumberComponent
from .config import RequestsServiceConfig
from .links import RequestLink
from .results import RequestItem, RequestList
from .service import RequestsService

__all__ = (
    "RequestNumberComponent",
    "RequestLink",
    "RequestItem",
    "RequestList",
    "RequestsService",
    "RequestsServiceConfig",
)
