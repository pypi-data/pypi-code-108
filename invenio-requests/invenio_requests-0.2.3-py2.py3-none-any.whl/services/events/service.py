# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
# Copyright (C) 2021 Northwestern University.
# Copyright (C) 2021 TU Wien.
#
# Invenio-Requests is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""RequestEvents Service."""

from invenio_access.permissions import system_process
from invenio_records_resources.services import RecordService
from invenio_records_resources.services.base.links import LinksTemplate
from invenio_records_resources.services.uow import (
    RecordCommitOp,
    RecordDeleteOp,
    unit_of_work,
)

from ...records.api import RequestEventType


class RequestEventsService(RecordService):
    """Request Events service."""

    @unit_of_work()
    def create(self, identity, request_id, data, uow=None):
        """Create a request event.

        :param request_id: Identifier of the request (data-layer id).
        :param identity: Identity of user creating the event.
        :param dict data: Input data according to the data schema.
        """
        request = self._get_request(request_id)
        permission = self._get_permission("create", data["type"])
        self.require_permission(identity, permission, request=request)

        # Validate data (if there are errors, .load() raises)
        data, errors = self.schema.load(
            data,
            context={"identity": identity},
        )

        # It's the components that save the actual data in the record.
        record = self.record_cls.create(
            {},
            request=request.model,
            request_id=str(request_id),
            type=data["type"],
        )

        creator = self._get_creator(identity)

        # Run components
        self.run_components(
            "create",
            identity=identity,
            record=record,
            request=request,
            data=data,
            created_by=creator,
            uow=uow,
        )

        # Persist record (DB and index)
        uow.register(RecordCommitOp(record, indexer=self.indexer))

        return self.result_item(
            self,
            identity,
            record,
            links_tpl=self.links_item_tpl,
        )

    def read(self, identity, id_):
        """Retrieve a record."""
        record = self._get_event(id_)
        request = self._get_request(record.request_id)

        # Same "read_event" permission for all types of events
        self.require_permission(identity, "read_event", request=request)

        return self.result_item(
            self,
            identity,
            record,
            links_tpl=self.links_item_tpl,
        )

    @unit_of_work()
    def update(self, identity, id_, data, revision_id=None, uow=None):
        """Update an event (except for type)."""
        record = self._get_event(id_)
        request = self._get_request(record.request.id)
        data["type"] = record.type  # this service method doesn't allow type change

        self.check_revision_id(record, revision_id)

        # Permissions
        permission = self._get_permission("update", record.type)
        self.require_permission(identity, permission, event=record)

        data, _ = self.schema.load(
            data,
            context=dict(
                identity=identity,
                record=record,
            ),
        )

        # Run components
        self.run_components(
            "update",
            identity=identity,
            record=record,
            data=data,
            uow=uow,
        )

        uow.register(RecordCommitOp(record, indexer=self.indexer))

        return self.result_item(
            self,
            identity,
            record,
            links_tpl=self.links_item_tpl,
        )

    @unit_of_work()
    def delete(self, identity, id_, revision_id=None, uow=None):
        """Delete an event from database and search indexes.

        Deleting a comment is wiping the content and marking it deleted.
        Deleting an accepted/cancelled/declined is just wiping the content.
        Deleting another event is really deleting them.

        We may want to add a parameter to assert a kind of event is deleted
        to prevent the weird semantic of using the comments REST API to
        delete an event (which is only possible for an admin anyway).
        """
        record = self._get_event(id_)
        request = self._get_request(record.request_id)

        self.check_revision_id(record, revision_id)

        # Permissions
        permission = self._get_permission("delete", record.type)
        self.require_permission(identity, permission, request=request, event=record)

        if record.type == RequestEventType.COMMENT.value:
            record["payload"]["content"] = ""
            record.type = RequestEventType.REMOVED.value
            uow.register(
                RecordCommitOp(record, indexer=self.indexer, index_refresh=True)
            )
        else:
            uow.register(
                RecordDeleteOp(
                    record, force=True, indexer=self.indexer, index_refresh=True
                )
            )

        # Even though we don't always completely remove the RequestEvent
        # we return as though we did.
        return True

    def search(self, identity, request_id, params=None, es_preference=None, **kwargs):
        """Search for events (optionally of request_id) matching the querystring."""
        params = params or {}
        params.setdefault("sort", "oldest")

        # Permissions
        request = self._get_request(request_id) if request_id else None
        self.require_permission(identity, "search_event", request=request)

        # Prepare and execute the search
        search = self._search(
            "search",
            identity,
            params,
            es_preference,
            permission_action="read_event",
            **kwargs,
        )
        if request_id:
            search = search.filter("term", request_id=str(request_id))
        search_result = search.execute()

        return self.result_list(
            self,
            identity,
            search_result,
            params,
            links_tpl=LinksTemplate(
                self.config.links_search,
                context={"request_id": request_id, "args": params},
            ),
            links_item_tpl=self.links_item_tpl,
        )

    # Utilities
    @property
    def request_cls(self):
        """Get associated request class."""
        return self.config.request_cls

    def _get_permission(self, action, event_type):
        """Get associated permission.

        Needed to distinguish between kinds of events.
        """
        if (
            (event_type == RequestEventType.COMMENT.value)
            and (action in ["create", "update", "delete"])
        ):
            return f"{action}_comment"

        if action == "create":
            if event_type == RequestEventType.ACCEPTED.value:
                return "action_accept"
            elif event_type == RequestEventType.DECLINED.value:
                return "action_decline"
            elif event_type == RequestEventType.CANCELLED.value:
                return "action_cancel"

        return f"{action}_event"

    def _get_request(self, request_id):
        """Get associated request."""
        return self.request_cls.get_record(request_id)

    def _get_event(self, event_id, with_deleted=True):
        """Get associated event_id."""
        return self.record_cls.get_record(event_id, with_deleted=with_deleted)

    def _get_creator(self, identity):
        """Get the creator dict from the identity."""
        if system_process in identity.provides:
            return None  # TODO: Change this for some agreed value
        else:
            return {"user": str(identity.id)}
