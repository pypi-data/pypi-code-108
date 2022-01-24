#
# Copyright 2021 DataRobot, Inc. and its affiliates.
#
# All rights reserved.
#
# DataRobot, Inc.
#
# This is proprietary source code of DataRobot, Inc. and its
# affiliates.
#
# Released under the terms of DataRobot Tool and Utility Agreement.
import trafaret as t

from datarobot._compat import Int, String
from datarobot.models.api_object import APIObject
from datarobot.utils.pagination import unpaginate
from datarobot.utils.waiters import wait_for_async_resolution


class ChangeRequest(APIObject):
    _path = "changeRequests/"

    _user_operations = t.Dict(
        {
            t.Key("can_update"): t.Bool(),
            t.Key("can_resolve"): t.Bool(),
            t.Key("can_cancel"): t.Bool(),
            t.Key("can_comment"): t.Bool(),
            t.Key("can_review"): t.Bool(),
        }
    ).ignore_extra("*")

    _converter = t.Dict(
        {
            t.Key("id"): String(),
            t.Key("entity_type"): String(),
            t.Key("entity_id"): String(),
            t.Key("action"): String(),
            t.Key("change"): t.Dict(allow_extra="*") | t.Null(),
            t.Key("change_version_id"): String(),
            t.Key("status"): String(),
            t.Key("auto_apply"): t.Bool(),
            t.Key("user_id"): String(),
            t.Key("user_name"): String(allow_blank=True) | t.Null(),
            t.Key("comment"): String(allow_blank=True),
            t.Key("num_approvals_required"): Int(),
            t.Key("created_at"): String(),
            t.Key("updated_at"): String(),
            t.Key("user_operations"): _user_operations,
        }
    ).ignore_extra("*")

    def __init__(
        self,
        id,
        entity_type,
        entity_id,
        action,
        change,
        change_version_id,
        status,
        auto_apply,
        user_id,
        user_name,
        comment,
        num_approvals_required,
        created_at,
        updated_at,
        user_operations,
    ):
        self.id = id
        self.entity_type = entity_type
        self.entity_id = entity_id
        self.action = action
        self.change = change
        self.change_version_id = change_version_id
        self.status = status
        self.auto_apply = auto_apply
        self.user_id = user_id
        self.user_name = user_name
        self.comment = comment
        self.num_approvals_required = num_approvals_required
        self.created_at = created_at
        self.updated_at = updated_at
        self.user_operations = user_operations

    def __repr__(self):
        return (
            u"{}(id={id}, "
            u"entity_type={entity_type}, "
            u"entity_id={entity_id}, "
            u"action={action}, "
            u"status={status})"
        ).format(
            self.__class__.__name__,
            id=self.id,
            entity_type=self.entity_type,
            entity_id=self.entity_id,
            action=self.action,
            status=self.status,
        )

    @classmethod
    def from_server_data(cls, data, keep_attrs=None):
        keep_attrs = set(keep_attrs or [])
        keep_attrs.add("change")
        return super(ChangeRequest, cls).from_server_data(data, keep_attrs)

    @classmethod
    def list(cls, entity_type, entity_id=None, statuses=None):
        """List accessible change requests with the given filters.

        Parameters
        ----------
        entity_type : str
            type of the entity to search change requests for.
        entity_id : str, optional
            ID if the entity to filter change requests by.
        statuses : list[str], optional
            list of change request statuses to filter change requests by.

        Returns
        -------
        list[ChangeRequest]
        """
        param = {"entity_type": entity_type}
        if entity_id:
            param["entity_id"] = entity_id
        if statuses:
            param["status"] = statuses

        data = unpaginate(cls._path, param, cls._client)
        return [cls.from_server_data(item) for item in data]

    @classmethod
    def get(cls, change_request_id):
        """Retrieve change request by ID.

        Parameters
        ----------
        change_request_id : str
            ID of the change request to retrieve.

        Returns
        -------
        ChangeRequest
        """
        path = "{}{}/".format(cls._path, change_request_id)
        return cls.from_location(path)

    @classmethod
    def create(cls, entity_type, entity_id, action, change, auto_apply=None, comment=None):
        """Create new change request.

        Parameters
        ----------
        entity_type : str
            type of the entity to request changes for.
        entity_id : str
            ID of the entity to request changes for.
        action : str
            action the request is intended to perform on the entity.
        change : dict
            change that the user wants to apply to the entity.
        auto_apply : bool, optional
            whether the change request should be automatically applied after being approved.
        comment : str, optional
            free form text description on the request.

        Returns
        -------
        ChangeRequest
            created change request.
        """
        payload = {
            "entity_type": entity_type,
            "entity_id": entity_id,
            "action": action,
            "change": change,
        }

        if auto_apply is not None:
            payload["auto_apply"] = auto_apply

        if comment is not None:
            payload["comment"] = comment

        response = cls._client.post(cls._path, data=payload)
        return cls.from_server_data(response.json())

    def update(self, change=None, auto_apply=None, comment=None):
        """Update the change request.

        Parameters
        ----------
        change : dict, optional
            new change to set for the request.
            Setting a new change updates the change version.
        auto_apply : bool, optional
            whether the change request should be automatically applied after being approved.
        comment : str, optional
            comment to replace the existing change request comment with.

        Returns
        -------
        ChangeRequest
            an instance of updated change request.
        """
        payload = {
            "change": change,
            "auto_apply": auto_apply,
            "comment": comment,
        }
        payload = {k: v for k, v in payload.items() if v is not None}

        if not payload:
            raise ValueError()

        path = "{}{}/".format(self._path, self.id)
        response = self._client.patch(path, data=payload)
        return self.from_server_data(response.json())

    def _set_status(self, status):
        """Update change request status.

        Returns
        -------
        ChangeRequest
            change request after the status change.
        """
        path = "{}{}/status/".format(self._path, self.id)
        response = self._client.patch(path, data={"status": status})
        wait_for_async_resolution(self._client, response.headers["Location"])
        return self.get(self.id)

    def cancel(self):
        """Cancel the change request.

        Returns
        -------
        ChangeRequest
            cancelled change request.
        """
        return self._set_status("cancelled")

    def resolve(self):
        """Resolve the change request.

        Apply the change, requested to the entity.
        Only approved change requests can be resolved.

        Returns
        -------
        ChangeRequest
            resolved change request.
        """
        return self._set_status("resolving")

    def approve(self, comment=None):
        """Approve the change request.

        A shortcut for creating a review on the change request with `approved` status.

        Parameters
        ----------
        comment : str, optional
            free form comment to explain the approval.

        Returns
        -------
        ChangeRequestReview
        """
        return ChangeRequestReview.create(self.id, "approved", self.change_version_id, comment)

    def request_changes(self, comment=None):
        """Request updates to the change request.

        A shortcut for creating a review on the change request with `changesRequested` status.

        Parameters
        ----------
        comment : str, optional
            free form comment to explain why the updates are requested.

        Returns
        -------
        ChangeRequestReview
        """
        return ChangeRequestReview.create(
            self.id, "changesRequested", self.change_version_id, comment
        )


class ChangeRequestReview(APIObject):
    _path = "changeRequests/{}/reviews/"
    _converter = t.Dict(
        {
            t.Key("id"): String(),
            t.Key("change_request_id"): String(),
            t.Key("change_version_id"): String(),
            t.Key("status"): String(),
            t.Key("comment"): String(allow_blank=True),
            t.Key("user_id"): String(),
            t.Key("user_name"): String(allow_blank=True) | t.Null(),
            t.Key("created_at"): String(),
        }
    ).ignore_extra("*")

    def __init__(
        self,
        id,
        change_request_id,
        change_version_id,
        status,
        comment,
        user_id,
        user_name,
        created_at,
    ):
        self.id = id
        self.change_request_id = change_request_id
        self.change_version_id = change_version_id
        self.status = status
        self.comment = comment
        self.user_id = user_id
        self.user_name = user_name
        self.created_at = created_at

    def __repr__(self):
        return (
            u"{}(change_request_id={change_request_id}, "
            u"status={status}, "
            u"comment='{comment}')"
        ).format(
            self.__class__.__name__,
            change_request_id=self.change_request_id,
            status=self.status,
            comment=self.comment,
        )

    @classmethod
    def list(cls, change_request_id):
        """List change request reviews.

        Parameters
        ----------
        change_request_id : str
            ID of the change request to list reviews for.

        Returns
        -------
        list[ChangeRequestReview]
        """
        param = {}
        url = cls._path.format(change_request_id)
        data = unpaginate(url, param, cls._client)
        return [cls.from_server_data(item) for item in data]

    @classmethod
    def create(cls, change_request_id, status, change_version_id, comment=None):
        """Add a review for the change request.

        Parameters
        ----------
        change_request_id : str
            ID of the change request to add review for.
        status : str
            review status to create.
        change_version_id : str
            ID of the changes version the review is associated with.
        comment : str, optional
            free form text description on the review.

        Returns
        -------
        ChangeRequestReview
        """
        payload = {
            "change_version_id": change_version_id,
            "status": status,
        }
        if comment is not None:
            payload["comment"] = comment

        url = cls._path.format(change_request_id)
        response = cls._client.post(url, data=payload)
        return cls.from_server_data(response.json())

    @classmethod
    def get(cls, change_request_id, review_id):
        """Retrieve a review by ID for the given change request.

        Parameters
        ----------
        change_request_id : str
            ID of the change request to retrieve review for.
        review_id : str
            ID of the review to retrieve.

        Returns
        -------
        ChangeRequestReview
        """
        url = cls._path.format(change_request_id)
        path = "{}{}/".format(url, review_id)
        return cls.from_location(path)
