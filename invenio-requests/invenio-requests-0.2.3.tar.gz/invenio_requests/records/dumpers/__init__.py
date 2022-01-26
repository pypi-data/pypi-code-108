# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 TU Wien.
#
# Invenio-Requests is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Elasticsearch dumpers, for transforming to and from versions to index."""

from .calculated import CalculatedFieldDumperExt

__all__ = (
    "CalculatedFieldDumperExt",
)
