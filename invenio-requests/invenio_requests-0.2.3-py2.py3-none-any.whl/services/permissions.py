# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
# Copyright (C) 2021 Northwestern University.
# Copyright (C) 2021 TU Wien.
#
# Invenio-Requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Request permissions."""

from elasticsearch_dsl import Q
from invenio_records_permissions import RecordPermissionPolicy
from invenio_records_permissions.generators import (
    AuthenticatedUser,
    Generator,
    SystemProcess,
)


class RequestCheckGenerator(Generator):
    """Generator with support for a request check function."""

    def __init__(self, check=None):
        """Constructor."""
        super().__init__()
        self._request_check_fn = check

    def _check_request(self, request):
        """Perform request check if such a function is defined."""
        if request is None:
            return False

        if self._request_check_fn is not None:
            return self._request_check_fn(request)

        return True


def _get_id(identity):
    """Get string id from identity."""
    for need in identity.provides:
        if need.method == 'id':
            return str(need.value)
    return ""


class Creator(RequestCheckGenerator):
    """Allows request makers."""

    def __init__(self, check=None, disable_query=False):
        """Constructor."""
        super().__init__(check)
        self.disable_query = disable_query

    def needs(self, request=None, **kwargs):
        """Enabling Needs."""
        if request is None:
            return []

        if self._check_request(request):
            creator = request.created_by
            if creator is not None and creator.get_need() is not None:
                return [creator.get_need()]

        return []

    def query_filter(self, identity=None, **kwargs):
        """Filters for current identity as owner."""
        if self.disable_query:
            return []

        if identity:
            # We assume creators are users for now
            user_id = _get_id(identity)
            return Q("term", **{"created_by.user": user_id})
        else:
            return []


class Receiver(RequestCheckGenerator):
    """Allows request Receiver."""

    def __init__(self, check=None, disable_query=False):
        """Constructor."""
        super().__init__(check)
        self.disable_query = disable_query

    def needs(self, request=None, **kwargs):
        """Enabling Needs.

        record is a request here
        """
        if request is None:
            return []

        if self._check_request(request):
            need = request.receiver.get_need()
            if need is not None:
                return [need]

        return []

    def query_filter(self, identity=None, **kwargs):
        """Filters for current identity as owner."""
        if self.disable_query:
            return []

        # It is up to community module to define community receivers
        if identity:
            user_id = _get_id(identity)
            return Q("term", **{"receiver.user": user_id})
        else:
            return []


def is_open(request):
    """Check if the request is open."""
    return request.is_open


def is_not_open(request):
    """Check if the request is closed or a draft."""
    return not request.is_open


def is_closed(request):
    """Check if the request is closed."""
    return request.is_closed


def is_not_closed(request):
    """Check if the request is open or a draft."""
    return not request.is_closed


def is_draft(request):
    """Check if the request is a draft (neither open nor closed)."""
    return not request.is_open and not request.is_closed


def is_no_draft(request):
    """Check if the request is not a draft (either open or closed)."""
    return request.is_open or request.is_closed


class Commenter(Generator):
    """Allows request event commenter."""

    def needs(self, event=None, **kwargs):
        """Enabling Needs."""
        return [event.created_by.get_need()]

        # TODO: events also need this kind of structure
        if event is None:
            return []

        creator = event.created_by
        if creator is not None and creator.get_need() is not None:
            return [creator.get_need()]

        return []

    def query_filter(self, identity=None, **kwargs):
        """Filters for current identity as creator."""
        users = [n.value for n in identity.provides if n.method == "id"]
        if users:
            return Q("terms", **{"created_by.user": users})


class AllowedSearcher(Generator):
    """Any user that was allowed by the corresponding can_search.

    This is a "cheat" originally created so that Events don't need to be indexed with a
    corresponding serialized Request. The can_search permission already restricts
    who can search and in the case of Events, those can see all Events.
    """

    def query_filter(self, identity=None, **kwargs):
        """Returns all and counts on service to filter by request_id."""
        return Q("match_all")


class PermissionPolicy(RecordPermissionPolicy):
    """Permission policy."""

    # TODO:
    # - require: if receiver is community AND community restricted:
    #   community <id> member (delegate to entity?)
    can_create = [AuthenticatedUser(), SystemProcess()]
    can_read = [Creator(), Receiver(check=is_open), SystemProcess()]
    can_update = [
        Creator(check=is_not_closed),
        Receiver(check=is_open),
        SystemProcess(),
    ]
    can_delete = [Creator(check=is_draft), SystemProcess()]
    # For search, recall that _what_ identities can see is defined by `can_read`
    can_search = [AuthenticatedUser(), SystemProcess()]

    # Actions: Submit/Cancel/Accept/Decline/Expire
    can_action_submit = [Creator(check=is_draft), SystemProcess()]
    can_action_cancel = [Creator(check=is_open), SystemProcess()]
    can_action_accept = [Receiver(check=is_open), SystemProcess()]
    can_action_decline = [Receiver(check=is_open), SystemProcess()]
    can_action_expire = [SystemProcess()]

    # Request Events: Comments
    can_create_comment = [Creator(), Receiver(check=is_no_draft), SystemProcess()]
    can_update_comment = [Commenter(), SystemProcess()]
    # Might need to revisit
    can_delete_comment = [Commenter(), Receiver(), SystemProcess()]

    # Request Events: All other events
    can_create_event = [SystemProcess()]
    can_read_event = [
        # this is a search over Events and not Requests so we disable the search
        Creator(disable_query=True),
        Receiver(check=is_no_draft, disable_query=True),
        AllowedSearcher(),
        SystemProcess(),
    ]
    can_update_event = [SystemProcess()]
    can_delete_event = [SystemProcess()]
    can_search_event = [Creator(), Receiver(check=is_no_draft), SystemProcess()]
