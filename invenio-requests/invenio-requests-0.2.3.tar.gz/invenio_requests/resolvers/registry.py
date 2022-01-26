# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2022 TU Wien.
# Copyright (C) 2021 CERN.
#
# Invenio-Requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Resolver and proxy for requests."""

from invenio_records_resources.references.registry import ResolverRegistryBase

from ..proxies import current_requests


class ResolverRegistry(ResolverRegistryBase):
    """Namespace for resolver functions."""

    @classmethod
    def get_registered_resolvers(cls):
        """Get all currently registered resolvers."""
        return iter(current_requests.entity_resolvers_registry)
