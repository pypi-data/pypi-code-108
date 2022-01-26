# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
# Copyright (C) 2021 TU Wien.
#
# Invenio-Requests is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio module for generic and customizable requests."""

from .base import RequestAction, RequestState
from .base import RequestType as BaseRequestType
from .default import DefaultRequestType

__all__ = (
    "BaseRequestType",
    "DefaultRequestType",
    "RequestAction",
    "RequestState",
)
