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

import dateutil
import pytest
import responses
import trafaret as t

from datarobot import Deployment
from datarobot.enums import (
    DEPLOYMENT_ACCURACY_HEALTH_STATUS,
    DEPLOYMENT_EXECUTION_ENVIRONMENT_TYPE,
    DEPLOYMENT_IMPORTANCE,
    DEPLOYMENT_MODEL_HEALTH_STATUS,
    DEPLOYMENT_SERVICE_HEALTH_STATUS,
)
from datarobot.models.deployment import DeploymentListFilters
from datarobot.utils import from_api
from tests.utils import request_body_to_json


def assert_deployment(deployment, deployment_data):
    def assert_health(health_from_client, health_from_api):
        assert health_from_client["status"] == health_from_client["status"]
        if "startDate" in health_from_api and health_from_api["startDate"]:
            timestamp = health_from_api["startDate"]
            assert health_from_client.get("start_date") == dateutil.parser.parse(timestamp)
        else:
            assert "start_date" not in health_from_client
        if "endDate" in health_from_api and health_from_api["endDate"]:
            timestamp = health_from_api["endDate"]
            assert health_from_client.get("end_date") == dateutil.parser.parse(timestamp)
        else:
            assert "end_date" not in health_from_client

    assert deployment.id == deployment_data["id"]
    assert deployment.label == deployment_data["label"]
    assert deployment.description == deployment_data["description"]

    assert deployment.model == from_api(deployment_data["model"])
    assert deployment.default_prediction_server == from_api(
        deployment_data["defaultPredictionServer"]
    )
    assert deployment.capabilities == from_api(deployment_data["capabilities"])
    assert deployment.permissions == deployment_data["permissions"]

    prediction_usage_from_api = deployment_data["predictionUsage"]
    assert deployment.prediction_usage["daily_rates"] == prediction_usage_from_api["dailyRates"]
    if prediction_usage_from_api["lastTimestamp"]:
        assert deployment.prediction_usage["last_timestamp"] == dateutil.parser.parse(
            prediction_usage_from_api["lastTimestamp"]
        )

    assert_health(deployment.service_health, deployment_data["serviceHealth"])
    assert_health(deployment.model_health, deployment_data["modelHealth"])
    assert_health(deployment.accuracy_health, deployment_data["accuracyHealth"])

    repr = "Deployment({label})".format(label=deployment_data["label"])
    assert str(deployment) == repr


@pytest.fixture()
def deployment_get_response(unittest_endpoint, deployments_data):
    for deployment_data in deployments_data:
        url = "{}/{}/{}/".format(unittest_endpoint, "deployments", deployment_data["id"])
        responses.add(
            responses.GET,
            url,
            status=200,
            content_type="application/json",
            body=json.dumps(deployment_data),
        )


@responses.activate
@pytest.mark.usefixtures("deployment_get_response")
def test_get_deployment(deployments_data):
    for deployment_data in deployments_data:
        deployment = Deployment.get(deployment_data["id"])
        assert_deployment(deployment, deployment_data)


class TestDeploymentDelete(object):
    @pytest.fixture()
    def deployment_delete_response(self, unittest_endpoint, deployments_data):
        for deployment_data in deployments_data:
            url = "{}/{}/{}/".format(unittest_endpoint, "deployments", deployment_data["id"])
            responses.add(responses.DELETE, url, status=204)

    @responses.activate
    @pytest.mark.usefixtures("deployment_get_response", "deployment_delete_response")
    def test_delete_deployment(self, deployment_data):
        deployment = Deployment.get(deployment_data["id"])
        deployment.delete()

        assert responses.calls[1].request.method == "DELETE"
        assert responses.calls[1].request.url.endswith("/deployments/5c6f7a9e9ca9b20017ff95a2/")


class TestDeploymentCreateFromLearningModel(object):
    @pytest.fixture
    def learning_model_create_response(self, unittest_endpoint, deployment_data):
        url = "{}/{}/{}/".format(unittest_endpoint, "deployments", "fromLearningModel")
        responses.add(
            responses.POST,
            url,
            body=json.dumps({"id": deployment_data["id"]}),
            status=200,
            content_type="application/json",
        )

    @responses.activate
    @pytest.mark.usefixtures("learning_model_create_response", "deployment_get_response")
    def test_create_minimum(self):
        Deployment.create_from_learning_model("5c76a543962d744efba25b85", "loan is bad")

        create_body = request_body_to_json(responses.calls[0].request)
        assert create_body["modelId"] == "5c76a543962d744efba25b85"
        assert create_body["label"] == "loan is bad"
        assert "description" not in create_body
        assert "defaultPredictionServerId" not in create_body

    @responses.activate
    @pytest.mark.usefixtures("learning_model_create_response", "deployment_get_response")
    def test_create_all_options(self):
        Deployment.create_from_learning_model(
            "5c76a543962d744efba25b85",
            "loan is bad",
            "predict if a loan is gonna default",
            "5c0fcdb8962d74370dd0c38e",
            "HIGH",
        )

        create_body = request_body_to_json(responses.calls[0].request)
        assert create_body["modelId"] == "5c76a543962d744efba25b85"
        assert create_body["label"] == "loan is bad"
        assert create_body["description"] == "predict if a loan is gonna default"
        assert create_body["defaultPredictionServerId"] == "5c0fcdb8962d74370dd0c38e"
        assert create_body["importance"] == "HIGH"


@pytest.mark.parametrize("from_version", [True, False])
class TestDeploymentCreateFromCustomModel(object):
    def _make_model_package_get_response(self, get_model_package_url, custom_model_entity_id, data):
        url = "{}?modelId={}".format(get_model_package_url, custom_model_entity_id)
        responses.add(
            responses.GET,
            url,
            status=200,
            content_type="application/json",
            body=json.dumps({"count": 1, "next": None, "previous": None, "data": data}),
        )

    @pytest.fixture
    def get_model_package_url(self, unittest_endpoint):
        return "{}/modelPackages/".format(unittest_endpoint)

    @pytest.fixture
    def create_model_package_url(self, unittest_endpoint, from_version):
        if from_version:
            route = "fromCustomModelVersion"
        else:
            route = "fromCustomModelImage"
        return "{}/modelPackages/{}/".format(unittest_endpoint, route)

    @pytest.fixture
    def get_deployment_url(self, unittest_endpoint):
        return "{}/deployments/".format(unittest_endpoint)

    @pytest.fixture
    def create_deployment_url(self, unittest_endpoint):
        return "{}/deployments/fromModelPackage/".format(unittest_endpoint)

    @pytest.fixture
    def get_status_url(self, unittest_endpoint):
        return "{}/status_url".format(unittest_endpoint)

    @pytest.fixture
    def custom_model_entity_id(self):
        return "5ea6aeeae8e8a40039714bde"

    @pytest.fixture
    def model_package_data(self):
        return {"id": "5eaaa09a40240308176cee55"}

    @pytest.fixture
    def prediction_server_id(self):
        return "5c0fcdb8962d74370dd0c38e"

    @pytest.fixture
    def importance(self):
        return "CRITICAL"

    @pytest.fixture
    def model_package_get_response(
        self, get_model_package_url, custom_model_entity_id, model_package_data
    ):
        self._make_model_package_get_response(
            get_model_package_url, custom_model_entity_id, [model_package_data]
        )

    @pytest.fixture
    def model_package_get_response_none(self, get_model_package_url, custom_model_entity_id):
        self._make_model_package_get_response(get_model_package_url, custom_model_entity_id, [])

    @pytest.fixture
    def model_package_create_response(self, create_model_package_url, model_package_data):
        responses.add(
            responses.POST,
            create_model_package_url,
            body=json.dumps(model_package_data),
            status=200,
            content_type="application/json",
        )

    @pytest.fixture
    def deployment_create_response(
        self, create_deployment_url, get_deployment_url, get_status_url, deployment_data
    ):
        responses.add(
            responses.POST,
            create_deployment_url,
            headers={"Location": get_status_url},
            body=json.dumps({"id": deployment_data["id"]}),
            status=200,
            content_type="application/json",
        )
        responses.add(
            responses.GET, get_status_url, headers={"Location": get_deployment_url}, status=303
        )

    @pytest.fixture
    def _assert_deployment_creation(
        self,
        model_package_data,
        deployment_data,
        prediction_server_id,
        importance,
        from_version,
        create_deployment_url,
        get_deployment_url,
        get_status_url,
    ):
        def _assert(
            create_deployment_req, get_status_req, get_deployment_req,
        ):
            assert create_deployment_req.method == "POST"
            assert create_deployment_req.url == create_deployment_url
            create_body = request_body_to_json(create_deployment_req)
            expected_body_attrs = {
                "modelPackageId",
                "label",
                "description",
                "defaultPredictionServerId",
            }
            if from_version:
                expected_body_attrs.add("importance")

            assert set(create_body) == expected_body_attrs
            assert create_body["modelPackageId"] == model_package_data["id"]
            assert create_body["label"] == "My deployment"
            assert create_body["description"] == "deployment description"
            assert create_body["defaultPredictionServerId"] == prediction_server_id

            if from_version:
                assert create_body["importance"] == importance

            assert get_status_req.method == "GET"
            assert get_status_req.url == get_status_url

            assert get_deployment_req.method == "GET"
            assert get_deployment_req.url == "{}{}/".format(
                get_deployment_url, deployment_data["id"]
            )

        return _assert

    @responses.activate
    @pytest.mark.usefixtures(
        "model_package_get_response", "deployment_create_response", "deployment_get_response"
    )
    def test_create_deployment_model_package_exists(
        self,
        custom_model_entity_id,
        prediction_server_id,
        importance,
        get_model_package_url,
        _assert_deployment_creation,
        from_version,
    ):
        args = [
            custom_model_entity_id,
            "My deployment",
            "deployment description",
            prediction_server_id,
        ]
        if from_version:
            Deployment.create_from_custom_model_version(*args, importance=importance)
        else:
            Deployment.create_from_custom_model_image(*args)

        assert len(responses.calls) == 4

        responses.calls[0].request.method == "GET"
        assert responses.calls[0].request.url == "{}?modelId={}".format(
            get_model_package_url, custom_model_entity_id
        )

        create_deployment_req = responses.calls[1].request
        get_status_req = responses.calls[2].request
        get_deployment_req = responses.calls[3].request

        _assert_deployment_creation(create_deployment_req, get_status_req, get_deployment_req)

    @responses.activate
    @pytest.mark.usefixtures(
        "model_package_get_response_none",
        "model_package_create_response",
        "deployment_create_response",
        "deployment_get_response",
    )
    def test_create_deployment_model_package_doesnt_exist(
        self,
        custom_model_entity_id,
        prediction_server_id,
        importance,
        get_model_package_url,
        create_model_package_url,
        _assert_deployment_creation,
        from_version,
    ):
        args = [
            custom_model_entity_id,
            "My deployment",
            "deployment description",
            prediction_server_id,
        ]
        if from_version:
            Deployment.create_from_custom_model_version(*args, importance=importance)
        else:
            Deployment.create_from_custom_model_image(*args)

        assert len(responses.calls) == 5

        # get model package
        assert responses.calls[0].request.method == "GET"
        assert responses.calls[0].request.url == "{}?modelId={}".format(
            get_model_package_url, custom_model_entity_id
        )

        # create model package
        assert responses.calls[1].request.method == "POST"
        assert responses.calls[1].request.url == create_model_package_url
        create_body = request_body_to_json(responses.calls[1].request)
        expected_field = "customModelVersionId" if from_version else "customModelImageId"
        assert set(create_body) == {expected_field}
        assert create_body[expected_field] == custom_model_entity_id

        create_deployment_req = responses.calls[2].request
        get_status_req = responses.calls[3].request
        get_deployment_req = responses.calls[4].request

        _assert_deployment_creation(create_deployment_req, get_status_req, get_deployment_req)


class TestDeploymentList(object):
    @pytest.fixture()
    def deployments_list_response_data(self, deployments_data):
        return {"count": 1, "next": None, "previous": None, "data": deployments_data}

    @pytest.fixture()
    def deployment_list_response(self, unittest_endpoint, deployments_list_response_data):
        url = "{}/{}/".format(unittest_endpoint, "deployments")
        responses.add(
            responses.GET,
            url,
            status=200,
            content_type="application/json",
            body=json.dumps(deployments_list_response_data),
        )

    @responses.activate
    @pytest.mark.usefixtures("deployment_list_response")
    def test_list_deployment(self, deployments_data):
        deployments_data = {item["id"]: item for item in deployments_data}
        deployments = Deployment.list()
        assert len(deployments) == len(deployments_data)
        for deployment in deployments:
            assert_deployment(deployment, deployments_data[deployment.id])

    @responses.activate
    @pytest.mark.usefixtures("deployment_list_response")
    def test_sort(self):
        Deployment.list(order_by="-label")
        assert "deployments/?orderBy=-label" in responses.calls[0].request.url

    @responses.activate
    @pytest.mark.usefixtures("deployment_list_response")
    def test_search(self):
        Deployment.list(search="readmitted")
        assert "deployments/?search=readmitted" in responses.calls[0].request.url

    @responses.activate
    @pytest.mark.usefixtures("deployment_list_response")
    @pytest.mark.parametrize(
        "filter_name,filter_value,query_param_key,query_param_value",
        [
            ("role", "OWNER", "role", "OWNER"),
            (
                "service_health",
                DEPLOYMENT_SERVICE_HEALTH_STATUS.PASSING,
                "serviceHealth",
                "passing",
            ),
            (
                "service_health",
                [DEPLOYMENT_SERVICE_HEALTH_STATUS.PASSING],
                "serviceHealth",
                "passing",
            ),
            (
                "service_health",
                [
                    DEPLOYMENT_SERVICE_HEALTH_STATUS.FAILING,
                    DEPLOYMENT_SERVICE_HEALTH_STATUS.WARNING,
                ],
                "serviceHealth",
                "failing,warning",
            ),
            ("model_health", DEPLOYMENT_MODEL_HEALTH_STATUS.PASSING, "modelHealth", "passing"),
            ("model_health", [DEPLOYMENT_MODEL_HEALTH_STATUS.FAILING], "modelHealth", "failing"),
            (
                "model_health",
                [DEPLOYMENT_MODEL_HEALTH_STATUS.PASSING, DEPLOYMENT_MODEL_HEALTH_STATUS.UNKNOWN],
                "modelHealth",
                "passing,unknown",
            ),
            (
                "accuracy_health",
                DEPLOYMENT_ACCURACY_HEALTH_STATUS.UNAVAILABLE,
                "accuracyHealth",
                "unavailable",
            ),
            (
                "accuracy_health",
                [DEPLOYMENT_ACCURACY_HEALTH_STATUS.WARNING],
                "accuracyHealth",
                "warning",
            ),
            (
                "accuracy_health",
                [
                    DEPLOYMENT_ACCURACY_HEALTH_STATUS.FAILING,
                    DEPLOYMENT_ACCURACY_HEALTH_STATUS.PASSING,
                ],
                "accuracyHealth",
                "failing,passing",
            ),
            (
                "importance",
                [DEPLOYMENT_IMPORTANCE.HIGH, DEPLOYMENT_IMPORTANCE.LOW],
                "importance",
                "HIGH,LOW",
            ),
        ],
    )
    def test_filters(self, filter_name, filter_value, query_param_key, query_param_value):
        filter_args = {filter_name: filter_value}
        filters = DeploymentListFilters(**filter_args)
        Deployment.list(filters=filters)

        expected_call = "deployments/?{}={}".format(
            query_param_key, query_param_value.replace(",", "%2C")
        )

        actual_call = responses.calls[0].request.url
        assert actual_call.endswith(
            expected_call
        ), "Expected called url to end with: {}\n Got: {}".format(expected_call, actual_call)

    @responses.activate
    @pytest.mark.usefixtures("deployment_list_response")
    def test_all_query_params(self):
        Deployment.list(
            order_by="-label",
            search="readmitted",
            filters=DeploymentListFilters(
                role="OWNER",
                service_health=DEPLOYMENT_SERVICE_HEALTH_STATUS.PASSING,
                model_health=DEPLOYMENT_MODEL_HEALTH_STATUS.WARNING,
                accuracy_health=DEPLOYMENT_ACCURACY_HEALTH_STATUS.FAILING,
                execution_environment_type=DEPLOYMENT_EXECUTION_ENVIRONMENT_TYPE.DATAROBOT,
            ),
        )
        expected_args = [
            "orderBy=-label",
            "search=readmitted",
            "role=OWNER",
            "serviceHealth=passing",
            "modelHealth=warning",
            "accuracyHealth=failing",
            "executionEnvironmentType=datarobot",
        ]
        query_param_str = responses.calls[0].request.url.split("deployments/?")[1]
        query_params = query_param_str.split("&")

        assert len(expected_args) == len(query_params)

        for expected_arg in expected_args:
            assert (
                expected_arg in query_params
            ), "Expected to find the query arg {}, but didn't.\n Got: {}".format(
                expected_arg, query_param_str
            )


class TestDeploymentUpdate(object):
    @pytest.fixture()
    def deployment_update_response(self, unittest_endpoint, deployments_data):
        for deployment_data in deployments_data:
            url = "{}/{}/{}/".format(unittest_endpoint, "deployments", deployment_data["id"])
            responses.add(responses.PATCH, url, status=204)

    @responses.activate
    @pytest.mark.usefixtures("deployment_get_response", "deployment_update_response")
    def test_cannot_update_nothing(self, deployment_data):
        deployment = Deployment.get(deployment_data["id"])
        with pytest.raises(ValueError):
            deployment.update()

    @responses.activate
    @pytest.mark.usefixtures("deployment_get_response", "deployment_update_response")
    def test_update_label(self, deployment_data):
        deployment = Deployment.get(deployment_data["id"])
        deployment.update(label="new label")

        assert responses.calls[1].request.method == "PATCH"
        assert responses.calls[1].request.url.endswith("/deployments/5c6f7a9e9ca9b20017ff95a2/")

        request_json = json.loads(responses.calls[1].request.body)
        assert request_json["label"] == "new label"

    @responses.activate
    @pytest.mark.usefixtures("deployment_get_response", "deployment_update_response")
    def test_update_description(self, deployment_data):
        deployment = Deployment.get(deployment_data["id"])
        deployment.update(description="new description")

        assert responses.calls[1].request.method == "PATCH"
        assert responses.calls[1].request.url.endswith("/deployments/5c6f7a9e9ca9b20017ff95a2/")

        request_json = json.loads(responses.calls[1].request.body)
        assert request_json["description"] == "new description"

    @responses.activate
    @pytest.mark.usefixtures("deployment_get_response", "deployment_update_response")
    def test_update_importance(self, deployment_data):
        deployment = Deployment.get(deployment_data["id"])
        deployment.update(importance="LOW")

        assert responses.calls[1].request.method == "PATCH"
        assert responses.calls[1].request.url.endswith("/deployments/5c6f7a9e9ca9b20017ff95a2/")

        request_json = json.loads(responses.calls[1].request.body)
        assert request_json["importance"] == "LOW"


class TestDeploymentListFilters(object):
    @pytest.mark.parametrize(
        "filter_name,valid_value",
        [
            ("role", "OWNER"),
            ("role", "USER"),
            ("service_health", DEPLOYMENT_SERVICE_HEALTH_STATUS.PASSING),
            ("service_health", [DEPLOYMENT_SERVICE_HEALTH_STATUS.UNKNOWN]),
            ("service_health", DEPLOYMENT_SERVICE_HEALTH_STATUS.ALL),
            ("model_health", DEPLOYMENT_MODEL_HEALTH_STATUS.FAILING),
            ("model_health", [DEPLOYMENT_MODEL_HEALTH_STATUS.WARNING]),
            ("model_health", DEPLOYMENT_MODEL_HEALTH_STATUS.ALL),
            ("accuracy_health", DEPLOYMENT_ACCURACY_HEALTH_STATUS.UNAVAILABLE),
            ("accuracy_health", [DEPLOYMENT_ACCURACY_HEALTH_STATUS.UNKNOWN]),
            ("accuracy_health", DEPLOYMENT_ACCURACY_HEALTH_STATUS.ALL),
            ("execution_environment_type", DEPLOYMENT_EXECUTION_ENVIRONMENT_TYPE.DATAROBOT),
            ("execution_environment_type", DEPLOYMENT_EXECUTION_ENVIRONMENT_TYPE.ALL),
            ("importance", DEPLOYMENT_IMPORTANCE.MODERATE),
            ("importance", DEPLOYMENT_IMPORTANCE.ALL),
        ],
    )
    def test_valid_filter_values(self, filter_name, valid_value):
        kwargs = {filter_name: valid_value}
        DeploymentListFilters(**kwargs)

    @pytest.mark.parametrize(
        "filter_name,invalid_value",
        [
            ("role", 1234),
            ("service_health", 1234),
            ("model_health", 1234),
            ("accuracy_health", 1234),
            ("execution_environment_type", 1234),
            ("importance", 1234),
        ],
    )
    def test_invalid_filter_values(self, filter_name, invalid_value):
        with pytest.raises(t.DataError):
            kwargs = {filter_name: invalid_value}
            DeploymentListFilters(**kwargs)
