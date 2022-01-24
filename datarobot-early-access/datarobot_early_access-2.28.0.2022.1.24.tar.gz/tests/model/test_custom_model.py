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
from copy import copy, deepcopy
import json
from tempfile import NamedTemporaryFile

import pytest
import responses
import six

from datarobot import CustomInferenceModel, TARGET_TYPE
from datarobot.enums import CUSTOM_MODEL_TARGET_TYPE
from datarobot.utils import underscorize
from tests.model.utils import assert_custom_model_version


@pytest.fixture
def mocked_inference_model(mocked_models):
    return mocked_models["data"][1]


@pytest.fixture
def mocked_inference_model_with_resources(mocked_models_with_resources):
    return deepcopy(mocked_models_with_resources["data"][1])


@pytest.fixture
def mocked_multiclass_inference_model(mocked_multiclass_models):
    return deepcopy(mocked_multiclass_models["data"][1])


@pytest.fixture
def mocked_unstructured_inference_model(mocked_unstructured_models):
    return deepcopy(mocked_unstructured_models["data"][1])


@pytest.fixture
def mocked_anomaly_inference_model(mocked_anomaly_models):
    return deepcopy(mocked_anomaly_models["data"][1])


@pytest.fixture
def mocked_inference_model_no_latest_version(mocked_inference_model):
    model = copy(mocked_inference_model)
    model["latestVersion"] = None
    return model


@pytest.fixture
def mocked_inference_model_with_deprecated_target_support(mocked_inference_model):
    model = deepcopy(mocked_inference_model)
    if model["targetType"] == TARGET_TYPE.BINARY:
        model["supportsBinaryClassification"] = True
    elif model["targetType"] == TARGET_TYPE.REGRESSION:
        model["supportsRegression"] = True
    return model


def assert_custom_model_common(model, model_json):
    assert model.id == model_json["id"]
    assert model.name == model_json["name"]
    assert model.description == model_json["description"]

    for expected_target_type in [
        TARGET_TYPE.BINARY,
        TARGET_TYPE.REGRESSION,
        TARGET_TYPE.MULTICLASS,
        TARGET_TYPE.UNSTRUCTURED,
        TARGET_TYPE.ANOMALY,
    ]:
        assert (model.target_type == expected_target_type) == (
            model_json["targetType"] == expected_target_type
        )

    if model_json["latestVersion"]:
        assert_custom_model_version(model.latest_version, model_json["latestVersion"])
    else:
        assert model.latest_version is None
    assert model.deployments_count == model_json["deploymentsCount"]
    assert model.created_by == model_json["createdBy"]
    assert model.updated_at == model_json["updated"]
    assert model.created_at == model_json["created"]


def assert_inference_model(model, model_json):
    assert_custom_model_common(model, model_json)
    assert model.language == model_json["language"]
    if model.target_type in CUSTOM_MODEL_TARGET_TYPE.REQUIRES_TARGET_NAME:
        assert model.target_name == model_json["targetName"]
    assert model.training_dataset_id == model_json["trainingDatasetId"]
    assert model.training_dataset_version_id == model_json["trainingDatasetVersionId"]
    assert model.training_data_file_name == model_json["trainingDataFileName"]
    assert (
        model.training_data_assignment_in_progress == model_json["trainingDataAssignmentInProgress"]
    )
    assert model.positive_class_label == model_json.get("positiveClassLabel")
    assert model.negative_class_label == model_json.get("negativeClassLabel")
    assert model.prediction_threshold == model_json.get("predictionThreshold")
    assert model.class_labels == model_json.get("classLabels")
    assert model.training_data_partition_column == model_json["trainingDataPartitionColumn"]
    assert model.network_egress_policy == model_json["networkEgressPolicy"]
    assert model.maximum_memory == model_json["maximumMemory"]
    assert model.replicas == model_json["replicas"]


def mock_get_response(url, response):
    responses.add(
        responses.GET, url, status=200, content_type="application/json", body=json.dumps(response),
    )


class TestCustomInferenceModel(object):
    @pytest.mark.parametrize(
        "model_data", ["mocked_inference_model", "mocked_inference_model_no_latest_version"]
    )
    def test_from_server_data(self, request, model_data):
        model_data = request.getfixturevalue(model_data)
        model = CustomInferenceModel.from_server_data(model_data)
        assert_inference_model(model, model_data)

    @responses.activate
    def test_get_version(self, mocked_inference_model, make_models_url):
        # arrange
        url = make_models_url(mocked_inference_model["id"])
        mock_get_response(url, mocked_inference_model)

        # act
        model = CustomInferenceModel.get(mocked_inference_model["id"])

        # assert
        assert_inference_model(model, mocked_inference_model)

        assert responses.calls[0].request.method == "GET"
        assert responses.calls[0].request.url == url

    @responses.activate
    def test_list_versions(self, make_models_url, mocked_inference_model):
        # arrange
        url = make_models_url() + "?customModelType=inference"
        mock_get_response(
            url,
            {
                "count": 1,
                "totalCount": 1,
                "next": None,
                "previous": None,
                "data": [mocked_inference_model],
            },
        )

        # act
        models = CustomInferenceModel.list()

        # assert
        assert len(models) == 1
        assert_inference_model(models[0], mocked_inference_model)

        assert responses.calls[0].request.method == "GET"
        assert responses.calls[0].request.url == url

    @responses.activate
    @pytest.mark.parametrize("labels_as_files", [True, False])
    def test_update(self, make_models_url, mocked_inference_model, labels_as_files):
        # arrange
        patch = {
            "description": "xx",
            "predictionThreshold": 0.1,
            "classLabels": ["hot dog", "burrito", "hoagie", "reuben"],
        }

        url = make_models_url(mocked_inference_model["id"])
        mock_get_response(url, mocked_inference_model)

        mocked_inference_model.update(patch)

        responses.add(
            responses.PATCH,
            url,
            status=200,
            content_type="application/json",
            body=json.dumps(mocked_inference_model),
        )

        # act
        model = CustomInferenceModel.get(mocked_inference_model["id"])
        with NamedTemporaryFile() as f:
            args = deepcopy(patch)
            if labels_as_files:
                f.write("\n".join(args.pop("classLabels")).encode("utf-8"))
                f.flush()
                args["classLabelsFile"] = f.name

            model.update(**{underscorize(k): v for k, v in args.items()})

        # assert
        assert_inference_model(model, mocked_inference_model)

        assert responses.calls[0].request.method == "GET"
        assert responses.calls[0].request.url == url
        assert responses.calls[1].request.method == "PATCH"
        assert responses.calls[1].request.url == url
        assert responses.calls[1].request.body == json.dumps(patch).encode()

    @responses.activate
    def test_refresh(self, make_models_url, mocked_inference_model):
        # arrange
        url = make_models_url(mocked_inference_model["id"])
        mock_get_response(url, mocked_inference_model)

        mocked_inference_model.update({"description": "xx", "predictionThreshold": 0.1})

        mock_get_response(url, mocked_inference_model)

        # act
        model = CustomInferenceModel.get(mocked_inference_model["id"])
        model.refresh()

        # assert
        assert_inference_model(model, mocked_inference_model)

        assert responses.calls[0].request.method == "GET"
        assert responses.calls[0].request.url == url
        assert responses.calls[1].request.method == "GET"
        assert responses.calls[1].request.url == url

    @responses.activate
    def test_delete(self, make_models_url, mocked_inference_model):
        url = make_models_url(mocked_inference_model["id"])

        mock_get_response(url, mocked_inference_model)
        responses.add(
            responses.DELETE, url, status=204, content_type="application/json",
        )

        model = CustomInferenceModel.get(mocked_inference_model["id"])
        model.delete()

        assert responses.calls[0].request.method == "GET"
        assert responses.calls[0].request.url == url
        assert responses.calls[1].request.method == "DELETE"
        assert responses.calls[1].request.url == url

    @responses.activate
    def test_download(self, make_models_url, mocked_inference_model, tmpdir):
        # arrange
        url = make_models_url(mocked_inference_model["id"])
        mock_get_response(url, mocked_inference_model)
        responses.add(
            responses.GET,
            url + "download/",
            status=200,
            content_type="application/json",
            body=b"content",
        )

        downloaded_file = tmpdir.mkdir("sub").join("download")
        downloaded_file_path = str(downloaded_file)

        # act
        model = CustomInferenceModel.get(mocked_inference_model["id"])
        model.download_latest_version(downloaded_file_path)

        # assert
        assert six.ensure_binary(downloaded_file.read()) == b"content"

        assert responses.calls[0].request.method == "GET"
        assert responses.calls[0].request.url == url
        assert responses.calls[1].request.method == "GET"
        assert responses.calls[1].request.url == url + "download/"

    @responses.activate
    def test_assign_training_data_non_blocking(
        self, unittest_endpoint, make_models_url, mocked_inference_model, tmpdir
    ):
        status_url = "{}/status_url".format(unittest_endpoint)

        mocked_inference_model["trainingDataAssignmentInProgress"] = False
        responses.add(
            responses.GET,
            make_models_url(mocked_inference_model["id"]),
            status=200,
            content_type="application/json",
            body=json.dumps(mocked_inference_model),
        )
        responses.add(
            responses.PATCH,
            make_models_url(mocked_inference_model["id"]) + "trainingData/",
            status=200,
            content_type="application/json",
            headers={"Location": status_url},
            body=json.dumps({"id": mocked_inference_model["id"]}),
        )
        mocked_inference_model["trainingDataAssignmentInProgress"] = True
        responses.add(
            responses.GET,
            make_models_url(mocked_inference_model["id"]),
            status=200,
            content_type="application/json",
            body=json.dumps(mocked_inference_model),
        )

        model = CustomInferenceModel.get(mocked_inference_model["id"])

        assert not model.training_data_assignment_in_progress
        model.assign_training_data("5ea6bbc7402403321d4e1fae", max_wait=None)

        assert model.training_data_assignment_in_progress

        assert responses.calls[0].request.method == "GET"
        assert responses.calls[0].request.url == make_models_url(mocked_inference_model["id"])
        assert responses.calls[1].request.method == "PATCH"
        assert (
            responses.calls[1].request.url
            == make_models_url(mocked_inference_model["id"]) + "trainingData/"
        )
        assert responses.calls[2].request.method == "GET"
        assert responses.calls[2].request.url == make_models_url(mocked_inference_model["id"])

    @responses.activate
    def test_assign_training_data_blocking(
        self, unittest_endpoint, make_models_url, mocked_inference_model, tmpdir
    ):
        status_url = "{}/status_url".format(unittest_endpoint)

        mocked_inference_model["trainingDataAssignmentInProgress"] = False
        responses.add(
            responses.GET,
            make_models_url(mocked_inference_model["id"]),
            status=200,
            content_type="application/json",
            body=json.dumps(mocked_inference_model),
        )
        responses.add(
            responses.PATCH,
            make_models_url(mocked_inference_model["id"]) + "trainingData/",
            status=200,
            content_type="application/json",
            headers={"Location": status_url},
            body=json.dumps({"id": mocked_inference_model["id"]}),
        )
        responses.add(
            responses.GET,
            status_url,
            status=303,
            content_type="application/json",
            headers={"Location": status_url},
        )
        responses.add(
            responses.GET,
            make_models_url(mocked_inference_model["id"]),
            status=200,
            content_type="application/json",
            body=json.dumps(mocked_inference_model),
        )

        model = CustomInferenceModel.get(mocked_inference_model["id"])

        assert not model.training_data_assignment_in_progress
        model.assign_training_data("5ea6bbc7402403321d4e1fae")

        assert not model.training_data_assignment_in_progress

        assert responses.calls[0].request.method == "GET"
        assert responses.calls[0].request.url == make_models_url(mocked_inference_model["id"])
        assert responses.calls[1].request.method == "PATCH"
        assert (
            responses.calls[1].request.url
            == make_models_url(mocked_inference_model["id"]) + "trainingData/"
        )
        assert responses.calls[2].request.method == "GET"
        assert responses.calls[2].request.url == status_url
        assert responses.calls[3].request.method == "GET"
        assert responses.calls[3].request.url == make_models_url(mocked_inference_model["id"])

    @responses.activate
    @pytest.mark.parametrize(
        "model_data",
        [
            "mocked_inference_model",
            "mocked_inference_model_no_latest_version",
            "mocked_inference_model_with_resources",
            "mocked_inference_model_with_deprecated_target_support",
        ],
    )
    def test_create(self, request, make_models_url, model_data):
        model_data = request.getfixturevalue(model_data)
        responses.add(
            responses.POST,
            make_models_url(),
            status=200,
            content_type="application/json",
            body=json.dumps(model_data),
        )

        model = CustomInferenceModel.create(
            model_data["name"],
            TARGET_TYPE.REGRESSION,
            model_data["targetName"],
            network_egress_policy=model_data["networkEgressPolicy"],
            maximum_memory=model_data["maximumMemory"],
            replicas=model_data["replicas"],
        )
        assert_inference_model(model, model_data)

        assert responses.calls[0].request.method == "POST"
        assert responses.calls[0].request.url == make_models_url()

    def test_create_model_without_target_name(self, mocked_inference_model):
        model_data = mocked_inference_model
        with pytest.raises(
            ValueError,
            match="target_name is required for custom models with target type Regression",
        ):
            CustomInferenceModel.create(
                model_data["name"],
                TARGET_TYPE.REGRESSION,
                network_egress_policy=model_data["networkEgressPolicy"],
                maximum_memory=model_data["maximumMemory"],
                replicas=model_data["replicas"],
            )

    @responses.activate
    @pytest.mark.parametrize("labels_as_files", [True, False])
    def test_create_with_multiclass_labels(
        self, mocked_multiclass_inference_model, make_models_url, labels_as_files
    ):
        model_data = mocked_multiclass_inference_model
        responses.add(
            responses.POST,
            make_models_url(),
            status=200,
            content_type="application/json",
            body=json.dumps(model_data),
        )

        if labels_as_files:
            with NamedTemporaryFile() as f:
                f.write("\n".join(model_data["classLabels"]).encode("utf-8"))
                f.flush()
                model = CustomInferenceModel.create(
                    model_data["name"],
                    TARGET_TYPE.MULTICLASS,
                    model_data["targetName"],
                    class_labels_file=f.name,
                    network_egress_policy=model_data["networkEgressPolicy"],
                    maximum_memory=model_data["maximumMemory"],
                    replicas=model_data["replicas"],
                )
        else:
            model = CustomInferenceModel.create(
                model_data["name"],
                TARGET_TYPE.MULTICLASS,
                model_data["targetName"],
                class_labels=model_data["classLabels"],
                network_egress_policy=model_data["networkEgressPolicy"],
                maximum_memory=model_data["maximumMemory"],
                replicas=model_data["replicas"],
            )
        assert_inference_model(model, model_data)

        assert responses.calls[0].request.method == "POST"
        assert responses.calls[0].request.url == make_models_url()
        assert (
            json.loads(responses.calls[0].request.body)["classLabels"] == model_data["classLabels"]
        )

    @responses.activate
    @pytest.mark.parametrize(
        "inference_model, target_type",
        [
            ["mocked_unstructured_inference_model", TARGET_TYPE.UNSTRUCTURED],
            ["mocked_anomaly_inference_model", TARGET_TYPE.ANOMALY],
        ],
    )
    def test_create_no_target_model(self, request, inference_model, target_type, make_models_url):
        model_data = request.getfixturevalue(inference_model)

        responses.add(
            responses.POST,
            make_models_url(),
            status=200,
            content_type="application/json",
            body=json.dumps(model_data),
        )

        model = CustomInferenceModel.create(
            model_data["name"],
            target_type,
            network_egress_policy=model_data["networkEgressPolicy"],
            maximum_memory=model_data["maximumMemory"],
            replicas=model_data["replicas"],
        )
        assert_inference_model(model, model_data)

        assert responses.calls[0].request.method == "POST"
        assert responses.calls[0].request.url == make_models_url()

    @responses.activate
    def test_create_copy(self, make_models_url, mocked_inference_model):
        custom_model_to_copy = "5ea6bbc7402403321d4e1fad"

        url = make_models_url() + "fromCustomModel/"
        responses.add(
            responses.POST,
            url,
            status=200,
            content_type="application/json",
            body=json.dumps(mocked_inference_model),
        )

        model = CustomInferenceModel.copy_custom_model(custom_model_to_copy)
        assert_inference_model(model, mocked_inference_model)

        req = responses.calls[0].request
        assert req.method == "POST"
        assert req.url == url
        assert json.loads(req.body) == {"customModelId": custom_model_to_copy}
