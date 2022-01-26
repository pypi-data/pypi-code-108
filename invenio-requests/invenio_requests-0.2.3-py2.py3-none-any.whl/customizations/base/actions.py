# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
# Copyright (C) 2021 TU Wien.
#
# Invenio-Requests is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Base class for customizable actions on requests."""

from ...errors import NoSuchActionError


class RequestAction:
    """Base class for actions on requests."""

    status_from = None
    """Required status of a request to run this action."""

    status_to = 'draft'
    """Status after execution of the action."""

    event_type = None
    """Defines an event type which will be logged if defined."""

    def __init__(self, request):
        """Constructor."""
        self.request = request

    def can_execute(self, identity):
        """Check whether the action can be executed.

        This is mostly intended to be a hook for checking prerequisites
        (think, for instance, CI/CD pipeline runs).
        :param identity: The identity of the executor.
        :return: True if the action can be executed, False otherwise.
        """
        return self.status_from is None or \
            self.request.status in self.status_from

    def execute(self, identity, uow):
        """Execute the request action.

        :param identity: The identity of the executor.
        :param data: The passed input to the action.
        """
        self.request.status = self.status_to


class RequestActions:
    """Namespace for RequestActions static calls."""

    @classmethod
    def get_action(cls, request, action_name):
        """Get the action registered under the given name.

        :param action_name: The registered name of the action.
        :return: The action registered under the given name.
        """
        try:
            return request.type.available_actions[action_name](request)
        except KeyError:
            raise NoSuchActionError(action=action_name)

    @classmethod
    def can_execute(cls, identity, request, action_name):
        """Check wether identity and request can execute action.

        Perhaps data is sometimes useful for that check, so also included.
        """
        return cls.get_action(request, action_name).can_execute(identity)

    @classmethod
    def execute(cls, identity, request, action_name, uow):
        """Have identity execute on request the action with the data."""
        return cls.get_action(request, action_name).execute(identity, uow)
