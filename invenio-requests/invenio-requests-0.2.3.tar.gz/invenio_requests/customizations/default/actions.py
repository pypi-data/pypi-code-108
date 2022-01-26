# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 TU Wien.
# Copyright (C) 2021 Northwestern University.
#
# Invenio-Requests is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RequestActions define code to be executed when performing actions on requests."""


from invenio_access.permissions import system_process

from ...records.api import RequestEventType
from ..base import RequestAction


class SubmitAction(RequestAction):
    """Submit a request."""

    status_from = ['draft']
    status_to = 'open'


class AcceptAction(RequestAction):
    """Decline a request."""

    status_from = ['open']
    status_to = 'accepted'
    event_type = RequestEventType.ACCEPTED.value


class DeclineAction(RequestAction):
    """Decline a request."""

    status_from = ['open']
    status_to = 'declined'
    event_type = RequestEventType.DECLINED.value


class CancelAction(RequestAction):
    """Cancel a request."""

    status_from = ['open']
    status_to = 'cancelled'
    event_type = RequestEventType.CANCELLED.value


class ExpireAction(RequestAction):
    """Expire a request."""

    status_from = ['open']
    status_to = 'expired'
    event_type = RequestEventType.EXPIRED.value

    def can_execute(self, identity):
        """Check whether the action can be executed."""
        is_system_process = system_process in identity.provides
        return super().can_execute(identity) and is_system_process
