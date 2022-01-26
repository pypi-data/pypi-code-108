# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
# Copyright (C) 2021 TU Wien.
# Copyright (C) 2021 Northwestern University.
#
# Invenio-Requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Resources module."""

from .events import RequestCommentsResource, RequestCommentsResourceConfig
from .requests import RequestsResource, RequestsResourceConfig

__all__ = (
    "RequestsResource",
    "RequestsResourceConfig",
    "RequestCommentsResource",
    "RequestCommentsResourceConfig",
)
