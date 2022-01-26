# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2022 TU Wien.
# Copyright (C) 2021 CERN.
#
# Invenio-Requests is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Base class for creating custom types of requests.

The `RequestType` classes are the most important part in the customization/extension
mechanism for custom types of requests.
TODO explain what can be done here, and how!
"""


import base32_lib as base32
import marshmallow as ma
from invenio_records_resources.services.references import EntityReferenceBaseSchema

from ...proxies import current_requests


class RequestType:
    """Base class for custom request types."""

    type_id = "base-request"
    """The unique and constant identifier for this type of requests.

    Since this property is used to map generic chunks of data from the database
    (i.e. the request model entries) to their correct `RequestType`, this should
    be a globally unique value.
    By convention, this would be the name of the package in which the custom
    `RequestType` is defined as prefix, together with a suffix related to the
    `RequestType`.
    Further, it should be constant after the first release of the package
    (otherwise, requests created with the old value will no longer be able to be
    mapped to their `RequestType`).
    """

    name = "Base Request"
    """The human-readable name for this type of requests."""

    available_statuses = {}
    """Available statuses for the Request.

    The keys in this dictionary is the set of available statuses, and their
    values are indicators whether this Request is still considered to be
    "open" in this state.
    """

    default_status = None
    """The default status for new requests of this type.

    This must be set to one of the available statuses for the custom request type.
    """

    available_actions = {}
    """Available actions for this Request.

    The keys are the internal identifiers for the actions, the values are
    the actual RequestAction classes (not objects).
    Whenever an action is looked up, a new object of the registered
    RequestAction class is instantiated with the current Request object as
    argument.
    """

    creator_can_be_none = True
    """Determines if the ``created_by`` reference accepts ``None``."""

    receiver_can_be_none = False
    """Determines if the ``receiver`` reference accepts ``None``."""

    topic_can_be_none = True
    """Determines if the ``topic`` reference accepts ``None``."""

    allowed_creator_ref_types = ["user"]
    """A list of allowed TYPE keys for ``created_by`` reference dicts."""

    allowed_receiver_ref_types = ["user"]
    """A list of allowed TYPE keys for ``receiver`` reference dicts."""

    allowed_topic_ref_types = []
    """A list of allowed TYPE keys for ``topic`` reference dicts."""

    payload_schema = None
    """Schema for supported payload fields.

    Define it as a dictionary of fields mapping:

    .. code-block:: python

        payload_schema = {
            "content": fields.String(),
            # ...
        }
    """

    @classmethod
    def _create_marshmallow_schema(cls):
        """Create a marshmallow schema for this request type."""
        # Avoid circular imports
        from invenio_requests.services.schemas import RequestSchema

        # The reference fields always need to be added
        RefBaseSchema = EntityReferenceBaseSchema
        additional_fields = {
            "created_by": ma.fields.Nested(
                RefBaseSchema.create_from_dict(cls.allowed_creator_ref_types),
                allow_none=cls.creator_can_be_none,
            ),
            "receiver": ma.fields.Nested(
                RefBaseSchema.create_from_dict(cls.allowed_receiver_ref_types),
                allow_none=cls.receiver_can_be_none,
            ),
            "topic": ma.fields.Nested(
                RefBaseSchema.create_from_dict(cls.allowed_topic_ref_types),
                allow_none=cls.topic_can_be_none,
            ),
        }

        # Raise on invalid payload keys
        class PayloadBaseSchema(ma.Schema):
            class Meta:
                unknown = ma.RAISE

        # If a payload schema is defined, add it to the request schema
        if cls.payload_schema is not None:
            additional_fields["payload"] = ma.fields.Nested(
                PayloadBaseSchema.from_dict(cls.payload_schema),
            )

        # Dynamically create a schema from the fields defined
        # by the payload schema dict.
        return RequestSchema.from_dict(additional_fields)

    @classmethod
    def marshmallow_schema(cls):
        """Create a schema for the entire request including payload."""
        type_id = cls.type_id
        if type_id not in current_requests._schema_cache:
            current_requests._schema_cache[type_id] = cls._create_marshmallow_schema()
        return current_requests._schema_cache[type_id]

    def generate_request_number(self, request, **kwargs):
        """Generate a new request number identifier.

        This method can be overridden in subclasses to create external identifiers
        according to a custom schema, using the information associated with the request
        (e.g. topic, receiver, creator).
        """
        from invenio_requests.records.models import RequestNumber

        return base32.encode(RequestNumber.next())

    def __str__(self):
        """Return str(self)."""
        # Value used by marshmallow schemas to represent the type.
        return self.type_id

    def __repr__(self):
        """Return repr(self)."""
        return f"<RequestType '{self.type_id}'>"
