# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 TU Wien.
#
# Invenio-Requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Request Resources module."""

from .config import RequestsResourceConfig
from .resource import RequestsResource

__all__ = (
    "RequestsResource",
    "RequestsResourceConfig",
)
