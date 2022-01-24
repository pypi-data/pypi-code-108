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
import json

import pytest
import responses

from datarobot.models import ChangeRequest
from tests.utils import request_body_to_json


def assert_change_request(change_request, change_request_data):
    assert change_request.id == change_request_data["id"]
    assert change_request.entity_type == change_request_data["entityType"]
    assert change_request.entity_id == change_request_data["entityId"]
    assert change_request.action == change_request_data["action"]
    assert change_request.change_version_id == change_request_data["changeVersionId"]
    assert change_request.status == change_request_data["status"]
    assert change_request.auto_apply == change_request_data["autoApply"]
    assert change_request.user_id == change_request_data["userId"]
    assert change_request.user_name == change_request_data["userName"]
    assert change_request.comment == change_request_data["comment"]
    assert change_request.num_approvals_required == change_request_data["numApprovalsRequired"]
    assert change_request.created_at == change_request_data["createdAt"]
    assert change_request.updated_at == change_request_data["updatedAt"]


def assert_change_request_review(review, review_data):
    assert review.id == review_data["id"]
    assert review.change_version_id == review_data["changeVersionId"]
    assert review.status == review_data["status"]
    assert review.comment == review_data["comment"]


@pytest.fixture
def change_requests_data():
    return [
        {
            "entityId": "618011c0f2fe42608a86c764",
            "entityType": "deployment",
            "action": "approve",
            "userId": "5ca19879a950d002c61ea3e7",
            "autoApply": True,
            "numApprovalsRequired": 1,
            "updatedAt": "2021-11-01 16:11:45.445000",
            "processedAt": None,
            "status": "pending",
            "statusChangedAt": None,
            "statusChangedBy": None,
            "changeVersionId": "0",
            "change": {"approvalStatus": "APPROVED"},
            "diff": {
                "base": {"approvalStatus": "PENDING"},
                "head": {"approvalStatus": "APPROVED"},
                "changesFrom": [],
                "changesTo": ["New deployment was created"],
            },
            "createdAt": "2021-11-01 16:11:45.445000",
            "id": "618011c1f2fe42608a86c76e",
            "userName": "oleksandr.pikovets@datarobot.com",
            "comment": "",
            "userOperations": {
                "canUpdate": True,
                "canResolve": False,
                "canCancel": True,
                "canComment": True,
                "canReview": False,
            },
        },
        {
            "entityId": "60a5261f916dac11dd73cb7f",
            "entityType": "deployment",
            "action": "delete",
            "userId": "5ca19879a950d002c61ea3e7",
            "autoApply": True,
            "numApprovalsRequired": 1,
            "updatedAt": "2021-09-14 11:19:38.613000",
            "processedAt": None,
            "status": "pending",
            "statusChangedAt": None,
            "statusChangedBy": None,
            "changeVersionId": "0",
            "change": None,
            "diff": {"changesFrom": [], "changesTo": ["Deployment will be deleted"]},
            "createdAt": "2021-09-14 11:19:38.613000",
            "id": "6140854af4577688789a358a",
            "userName": "oleksandr.pikovets@datarobot.com",
            "comment": "",
            "userOperations": {
                "canUpdate": True,
                "canResolve": False,
                "canCancel": True,
                "canComment": True,
                "canReview": False,
            },
        },
        {
            "entityId": "60a38bc016b75b5fc73c6c39",
            "entityType": "deployment",
            "action": "changeImportance",
            "userId": "5ca19879a950d002c61ea3e7",
            "autoApply": False,
            "numApprovalsRequired": 1,
            "updatedAt": "2021-12-15 12:30:28.088000",
            "processedAt": "2021-12-15 13:59:38.361000",
            "status": "cancelled",
            "statusChangedAt": None,
            "statusChangedBy": None,
            "changeVersionId": "0",
            "change": {"importance": "CRITICAL"},
            "diff": {
                "base": {"importance": "LOW"},
                "head": {"importance": "CRITICAL"},
                "changesFrom": ["Low importance"],
                "changesTo": ["Critical importance"],
            },
            "createdAt": "2021-12-15 12:30:28.088000",
            "id": "61b9dfe4c7d1c1da3bf9c992",
            "userName": "oleksandr.pikovets@datarobot.com",
            "comment": "",
            "userOperations": {
                "canUpdate": False,
                "canResolve": False,
                "canCancel": False,
                "canComment": False,
                "canReview": False,
            },
        },
    ]


@pytest.fixture(params=[0, 1, 2])
def change_request_data_index(request):
    return request.param


@pytest.fixture
def change_request_response_data(change_requests_data, change_request_data_index):
    return change_requests_data[change_request_data_index]


@pytest.fixture
def change_request_id(change_request_response_data):
    return change_request_response_data["id"]


@pytest.fixture(params=["approved", "changesRequested"])
def review_response_data(request, change_request_response_data):
    return {
        "id": "5ca19879a950d002c61ea3e7",
        "changeRequestId": change_request_response_data["id"],
        "changeVersionId": change_request_response_data["changeVersionId"],
        "comment": "Reviewed",
        "status": request.param,
        "userId": "5ca19879a950d002c61ea3e7",
        "userName": "oleksandr.pikovets+mlops.admin@datarobot.com",
        "createdAt": "2021-12-15 12:40:28.088000",
    }


@pytest.fixture
def change_request_get_response(unittest_endpoint, change_request_id, change_request_response_data):
    url = "{}/{}/{}/".format(unittest_endpoint, "changeRequests", change_request_id)
    responses.add(
        responses.GET, url, json=change_request_response_data, status=200,
    )


def test_change_request_repr():
    change_request = ChangeRequest(
        id="changeRequestId1",
        entity_type="deployment",
        entity_id="deploymentId1",
        action="changeImportance",
        status="pending",
        change=None,
        change_version_id=None,
        auto_apply=None,
        user_id=None,
        user_name=None,
        comment=None,
        num_approvals_required=None,
        created_at=None,
        updated_at=None,
        user_operations=None,
    )
    assert str(change_request) == (
        "ChangeRequest(id=changeRequestId1, "
        "entity_type=deployment, "
        "entity_id=deploymentId1, "
        "action=changeImportance, "
        "status=pending)"
    )


class TestChangeRequestList(object):
    @pytest.fixture()
    def change_requests_list_response_data(self, change_requests_data):
        return {
            "next": None,
            "previous": None,
            "totalCount": 3,
            "count": 3,
            "data": change_requests_data,
        }

    @pytest.fixture()
    def change_requests_list_response(self, unittest_endpoint, change_requests_list_response_data):
        url = "{}/{}/".format(unittest_endpoint, "changeRequests")
        responses.add(
            responses.GET,
            url,
            status=200,
            content_type="application/json",
            body=json.dumps(change_requests_list_response_data),
        )

    @responses.activate
    @pytest.mark.usefixtures("change_requests_list_response")
    def test_list_change_requests(self, change_requests_data):
        change_requests_data = {item["id"]: item for item in change_requests_data}
        change_requests = ChangeRequest.list("deployment")

        assert len(responses.calls) == 1

        list_request = responses.calls[0].request
        assert "changeRequests/?entityType=deployment" in list_request.url

        assert len(change_requests) == len(change_requests_data)
        for change_request in change_requests:
            assert_change_request(change_request, change_requests_data[change_request.id])


class TestChangeRequestGet(object):
    @responses.activate
    @pytest.mark.usefixtures("change_request_get_response")
    def test_get_change_request(
        self, unittest_endpoint, change_request_id, change_request_response_data
    ):
        change_request = ChangeRequest.get(change_request_id)

        assert len(responses.calls) == 1

        get_request = responses.calls[0].request
        assert get_request.method == "GET"
        assert get_request.url == "{}/changeRequests/{}/".format(
            unittest_endpoint, change_request_id
        )
        assert_change_request(change_request, change_request_response_data)


class TestChangeRequestCreate(object):
    @pytest.fixture
    def change_request_create_response(self, unittest_endpoint, change_request_response_data):
        url = "{}/{}/".format(unittest_endpoint, "changeRequests")
        responses.add(
            responses.POST, url, json=change_request_response_data, status=201,
        )

    @responses.activate
    @pytest.mark.usefixtures("change_request_create_response")
    def test_create_change_request(self, unittest_endpoint, change_request_response_data):
        action = change_request_response_data["action"]
        change = change_request_response_data["change"]
        change_request = ChangeRequest.create(
            "deployment", "60a5261f916dac11dd73cb7f", action, change, auto_apply=False, comment=""
        )

        assert len(responses.calls) == 1

        create_request = responses.calls[0].request
        assert create_request.method == "POST"
        assert create_request.url == "{}/changeRequests/".format(unittest_endpoint)

        create_body = request_body_to_json(create_request)
        expected_body = {
            "entityType": "deployment",
            "entityId": "60a5261f916dac11dd73cb7f",
            "action": action,
            "autoApply": False,
            "comment": "",
        }
        if change:
            expected_body["change"] = change

        assert create_body == expected_body
        assert_change_request(change_request, change_request_response_data)


class TestChangeRequestUpdate(object):
    @pytest.fixture
    def change_request_update_response(self, unittest_endpoint, change_request_response_data):
        change_request_id = change_request_response_data["id"]
        url = "{}/{}/{}/".format(unittest_endpoint, "changeRequests", change_request_id)
        responses.add(
            responses.PATCH, url, json=change_request_response_data, status=200,
        )

    @responses.activate
    @pytest.mark.usefixtures("change_request_update_response")
    def test_update_change_request(self, unittest_endpoint, change_request_response_data):
        change_request = ChangeRequest.from_server_data(change_request_response_data)
        updated_request = change_request.update(
            change={"importance": "CRITICAL"}, auto_apply=True, comment="Update comment"
        )

        assert change_request is not updated_request
        assert len(responses.calls) == 1

        update_request = responses.calls[0].request
        assert update_request.method == "PATCH"
        assert update_request.url == "{}/changeRequests/{}/".format(
            unittest_endpoint, change_request.id
        )

        update_body = request_body_to_json(update_request)
        assert update_body == {
            "change": {"importance": "CRITICAL"},
            "autoApply": True,
            "comment": "Update comment",
        }

        assert_change_request(updated_request, change_request_response_data)

    def test_update_change_request_error_if_no_updates(self, change_request_response_data):
        change_request = ChangeRequest.from_server_data(change_request_response_data)
        with pytest.raises(ValueError):
            change_request.update()


@pytest.fixture
def get_status_url(unittest_endpoint):
    return "{}/status_url".format(unittest_endpoint)


@pytest.fixture
def get_deployments_url(unittest_endpoint):
    return "{}/deployments/".format(unittest_endpoint)


class TestChangeRequestCancel(object):
    @pytest.fixture
    def change_request_cancel_response(
        self, unittest_endpoint, change_request_response_data, get_status_url, get_deployments_url
    ):
        change_request_id = change_request_response_data["id"]
        url = "{}/{}/{}/status/".format(unittest_endpoint, "changeRequests", change_request_id)
        responses.add(
            responses.PATCH,
            url,
            status=202,
            json={"status": "cancelled"},
            headers={"Location": get_status_url},
        )
        responses.add(
            responses.GET, get_status_url, headers={"Location": get_deployments_url}, status=303
        )

    @responses.activate
    @pytest.mark.usefixtures("change_request_cancel_response", "change_request_get_response")
    def test_cancel_change_request(
        self, unittest_endpoint, change_request_id, change_request_response_data
    ):
        change_request = ChangeRequest.from_server_data(change_request_response_data)

        cancelled_change_request = change_request.cancel()

        assert cancelled_change_request is not change_request
        assert len(responses.calls) == 3

        patch_request = responses.calls[0].request
        assert patch_request.method == "PATCH"
        assert patch_request.url == "{}/changeRequests/{}/status/".format(
            unittest_endpoint, change_request_id
        )

        patch_body = request_body_to_json(patch_request)
        assert patch_body == {"status": "cancelled"}

        assert_change_request(cancelled_change_request, change_request_response_data)


class TestChangeRequestResolve(object):
    @pytest.fixture
    def change_request_resolve_response(
        self, unittest_endpoint, change_request_response_data, get_status_url, get_deployments_url
    ):
        change_request_id = change_request_response_data["id"]
        url = "{}/{}/{}/status/".format(unittest_endpoint, "changeRequests", change_request_id)
        responses.add(
            responses.PATCH,
            url,
            status=202,
            json={"status": "resolving"},
            headers={"Location": get_status_url},
        )
        responses.add(
            responses.GET, get_status_url, headers={"Location": get_deployments_url}, status=303
        )

    @responses.activate
    @pytest.mark.usefixtures("change_request_resolve_response", "change_request_get_response")
    def test_resolve_change_request(
        self, unittest_endpoint, change_request_id, change_request_response_data
    ):
        change_request = ChangeRequest.from_server_data(change_request_response_data)

        cancelled_change_request = change_request.resolve()

        assert cancelled_change_request is not change_request
        assert len(responses.calls) == 3

        patch_request = responses.calls[0].request
        assert patch_request.method == "PATCH"
        assert patch_request.url == "{}/changeRequests/{}/status/".format(
            unittest_endpoint, change_request_id
        )

        patch_body = request_body_to_json(patch_request)
        assert patch_body == {"status": "resolving"}

        assert_change_request(cancelled_change_request, change_request_response_data)


class TestChangeRequestAddReview(object):
    @pytest.fixture
    def change_request_add_review_response(
        self, unittest_endpoint, change_request_response_data, review_response_data
    ):
        change_request_id = change_request_response_data["id"]
        url = "{}/{}/{}/reviews/".format(unittest_endpoint, "changeRequests", change_request_id)
        responses.add(responses.POST, url, status=201, json=review_response_data)

    @responses.activate
    @pytest.mark.usefixtures("change_request_add_review_response")
    def test_approve_change_request(
        self,
        unittest_endpoint,
        change_request_response_data,
        change_request_id,
        review_response_data,
    ):
        change_request = ChangeRequest.from_server_data(change_request_response_data)

        review = change_request.approve()

        assert len(responses.calls) == 1

        post_request = responses.calls[0].request
        assert post_request.method == "POST"
        assert post_request.url == "{}/changeRequests/{}/reviews/".format(
            unittest_endpoint, change_request_id
        )

        post_body = request_body_to_json(post_request)
        assert post_body == {
            "changeVersionId": change_request.change_version_id,
            "status": "approved",
        }
        assert_change_request_review(review, review_response_data)

    @responses.activate
    @pytest.mark.usefixtures("change_request_add_review_response")
    def test_request_change_to_change_request(
        self,
        unittest_endpoint,
        change_request_response_data,
        change_request_id,
        review_response_data,
    ):
        change_request = ChangeRequest.from_server_data(change_request_response_data)

        review = change_request.request_changes("Please apply manually")

        assert len(responses.calls) == 1

        post_request = responses.calls[0].request
        assert post_request.method == "POST"
        assert post_request.url == "{}/changeRequests/{}/reviews/".format(
            unittest_endpoint, change_request_id
        )

        post_body = request_body_to_json(post_request)
        assert post_body == {
            "changeVersionId": change_request.change_version_id,
            "status": "changesRequested",
            "comment": "Please apply manually",
        }
        assert_change_request_review(review, review_response_data)
