# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
# Copyright (C) 2021 TU Wien.
#
# Invenio-Requests is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Helpers for customizing the configuration in a controlled manner."""

# NOTE: Overall these classes should be refactored to be simply instantiations
# of the config class instead (e.g. "RDMRecordServiceConfig(...)"). However,
# that requires changing the pattern used also in Invenio-Drafts-Resources and
# Invenio-Records-Resources so we have a consistent way of instantiating
# configs.


def _make_cls(cls, attrs):
    """Make the custom config class."""
    return type(
        f"Custom{cls.__name__}",
        (cls,),
        attrs,
    )


class RequestsConfigMixin:
    """Shared customization for requests service config."""

    @classmethod
    def customize(cls, permission_policy=None):
        """Customize the service config with the given properties."""
        attrs = {}

        # permission policy
        if permission_policy is not None:
            attrs["permission_policy_cls"] = permission_policy

        # create the config class
        return _make_cls(cls, attrs) if attrs else cls
