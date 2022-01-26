# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2022 TU Wien.
#
# Invenio-Requests is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Systemfield for managing referenced entities in request."""

from functools import partial

from invenio_records_resources.records.systemfields.entity_reference import (
    ReferencedEntityField,
    check_allowed_references,
)

from ...resolvers.registry import ResolverRegistry

EntityReferenceField = partial(
    ReferencedEntityField, resolver_registry=ResolverRegistry
)
"""An opinionated ReferenceEntityField with set ResolverRegistry."""

check_allowed_creators = partial(
    check_allowed_references,
    lambda r: r.type.creator_can_be_none,
    lambda r: r.type.allowed_creator_ref_types,
)
"""Check function specific for the ``created_by`` field of requests."""

check_allowed_receivers = partial(
    check_allowed_references,
    lambda r: r.type.receiver_can_be_none,
    lambda r: r.type.allowed_receiver_ref_types,
)
"""Check function specific for the ``receiver`` field of requests."""

check_allowed_topics = partial(
    check_allowed_references,
    lambda r: r.type.topic_can_be_none,
    lambda r: r.type.allowed_topic_ref_types,
)
"""Check function specific for the ``topic`` field of requests."""
