# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 TU Wien.
#
# Invenio-Requests is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Enum for the various open states a request can have."""


from enum import Enum


class RequestState(Enum):
    """Enum for the various open states a request can have."""

    OPEN = "open"
    CLOSED = "closed"
    NEITHER = "neither"
