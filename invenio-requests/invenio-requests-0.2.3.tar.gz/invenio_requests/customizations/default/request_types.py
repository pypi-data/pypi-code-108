# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 TU Wien.
#
# Invenio-Requests is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Base class for creating custom types of requests.

The `RequestType` classes are the most important part in the customization/extension
mechanism for custom types of requests.
TODO explain what can be done here, and how!
"""


from ..base import RequestState, RequestType
from .actions import (
    AcceptAction,
    CancelAction,
    DeclineAction,
    ExpireAction,
    SubmitAction,
)


class DefaultRequestType(RequestType):
    """Base class for custom request types."""

    type_id = "default-request"
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

    name = "Default Request"
    """The human-readable name for this type of requests."""

    available_statuses = {
        "draft": RequestState.NEITHER,
        "open": RequestState.OPEN,
        "cancelled": RequestState.CLOSED,
        "declined": RequestState.CLOSED,
        "accepted": RequestState.CLOSED,
        "expired": RequestState.CLOSED,
    }
    """Available statuses for the Request.

    The keys in this dictionary is the set of available statuses, and their
    values are indicators whether this Request is still considered to be
    "open" in this state.
    """

    default_status = "draft"
    """The default status for new requests of this type.

    This must be set to one of the available statuses for the custom request type.
    """

    available_actions = {
        "submit": SubmitAction,
        "accept": AcceptAction,
        "cancel": CancelAction,
        "decline": DeclineAction,
        "expire": ExpireAction,
    }
    """Available actions for this Request.

    The keys are the internal identifiers for the actions, the values are
    the actual RequestAction classes (not objects).
    Whenever an action is looked up, a new object of the registered
    RequestAction class is instantiated with the current Request object as
    argument.
    """
