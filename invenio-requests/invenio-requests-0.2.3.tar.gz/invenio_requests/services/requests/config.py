# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
# Copyright (C) 2021 Northwestern University.
# Copyright (C) 2021 TU Wien.
#
# Invenio-Requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Requests service configuration."""

from invenio_records_resources.services import RecordServiceConfig, SearchOptions
from invenio_records_resources.services.records.links import pagination_links

from ...customizations.base import RequestActions
from ...records.api import Request
from ..permissions import PermissionPolicy
from .components import (
    DefaultStatusComponent,
    EntityReferencesComponent,
    RequestDataComponent,
    RequestNumberComponent,
)
from .customization import RequestsConfigMixin
from .links import RequestLink
from .params import ReferenceFilterParam
from .results import RequestItem, RequestList


def _is_action_available(request, context):
    """Check if the given action is available on the request."""
    action = context.get("action")
    identity = context.get("identity")
    return RequestActions.can_execute(identity, request, action)


class RequestSearchOptions(SearchOptions):
    """Search options."""

    params_interpreters_cls = SearchOptions.params_interpreters_cls + [
        ReferenceFilterParam.factory(param="created_by", field="created_by"),
        ReferenceFilterParam.factory(param="receiver", field="receiver"),
        ReferenceFilterParam.factory(param="topic", field="topic"),
    ]


class RequestsServiceConfig(RecordServiceConfig, RequestsConfigMixin):
    """Requests service configuration."""

    # common configuration
    permission_policy_cls = PermissionPolicy
    result_item_cls = RequestItem
    result_list_cls = RequestList
    search = RequestSearchOptions

    # request-specific configuration
    record_cls = Request  # needed for model queries
    schema = None  # stored in the API classes, for customization
    index_dumper = None

    # links configuration
    links_item = {
        "self": RequestLink("{+api}/requests/{id}"),
        "comments": RequestLink("{+api}/requests/{id}/comments"),
        "timeline": RequestLink("{+api}/requests/{id}/timeline"),
    }
    links_search = pagination_links("{+api}/requests{?args*}")
    action_link = RequestLink(
        "{+api}/requests/{id}/actions/{action}", when=_is_action_available
    )

    components = [
        # Order of components are important!
        RequestDataComponent,
        DefaultStatusComponent,
        EntityReferencesComponent,
        RequestNumberComponent,
    ]
