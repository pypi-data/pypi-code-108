# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
# Copyright (C) 2021 Northwestern University.
# Copyright (C) 2021 TU Wien.
#
# Invenio-Requests is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Request Events Service Config."""

from invenio_records_resources.services import RecordServiceConfig
from invenio_records_resources.services.base.links import Link
from invenio_records_resources.services.records.components import DataComponent
from invenio_records_resources.services.records.links import pagination_links
from invenio_records_resources.services.records.results import RecordItem

from ...records.api import Request, RequestEvent
from ..permissions import PermissionPolicy
from ..requests.components import EntityReferencesComponent
from ..schemas import RequestEventSchema
from .customization import CustomizationConfigMixin


class RequestEventItem(RecordItem):
    """RequestEvent result item."""

    @property
    def id(self):
        """Id property."""
        return self._record.id


class RequestEventLink(Link):
    """Link variables setter for RequestEvent links."""

    @staticmethod
    def vars(record, vars):
        """Variables for the URI template."""
        vars.update({"id": record.id, "request_id": record.request_id})


class RequestEventsServiceConfig(RecordServiceConfig, CustomizationConfigMixin):
    """Config."""

    request_cls = Request
    permission_policy_cls = PermissionPolicy
    schema = RequestEventSchema
    record_cls = RequestEvent
    components = [
        DataComponent,
        EntityReferencesComponent,  # only used for created_by
    ]
    result_item_cls = RequestEventItem

    # ResultItem configurations
    links_item = {
        "self": RequestEventLink("{+api}/requests/{request_id}/comments/{id}"),
    }
    links_search = pagination_links("{+api}/requests/{request_id}/timeline{?args*}")
