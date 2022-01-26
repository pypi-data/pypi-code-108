# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
# Copyright (C) 2021 TU Wien.
#
# Invenio-Requests is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Base classes for request customization."""

from .actions import RequestAction, RequestActions
from .request_types import RequestType
from .states import RequestState

__all__ = (
    "RequestAction",
    "RequestActions",
    "RequestType",
    "RequestState",
)
