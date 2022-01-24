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
import os
import tempfile
import unittest

import mock
import pytest
import responses
import six

import datarobot as dr
from datarobot.client import Client, get_client, set_client
from datarobot.enums import DEFAULT_TIMEOUT
from datarobot.errors import AppPlatformError, ClientError
from datarobot.rest import RESTClientObject, Retry
from tests.utils import SDKTestcase

if six.PY3:
    from unittest.mock import patch
else:
    from mock import patch


@pytest.mark.no_client
class TestClient(object):
    @pytest.mark.usefixtures("no_client_version_check")
    def test_instantiation(self):
        """
        Basic client installation.
        """
        client = Client(token="t-token", endpoint="https://host_name.com")
        assert get_client() is client

    @pytest.mark.usefixtures("no_client_version_check")
    @mock.patch("datarobot.client._file_exists", return_value=False)
    def test_instantiation_without_env(self, _):
        """
        Basic client installation by get_client without configuration.
        """
        with mock.patch("os.environ", {"DATAROBOT_ENDPOINT": "https://host_name.com"}):
            with pytest.raises(ValueError):
                get_client()

    @pytest.mark.usefixtures("no_client_version_check")
    @mock.patch("datarobot.client._file_exists")
    def test_no_endpoint_fails(self, mock_file_exists):
        mock_file_exists.return_value = False
        with mock.patch("os.environ", {}):
            with pytest.raises(ValueError):
                Client(token="NOTATOKEN")

    @pytest.mark.usefixtures("no_client_version_check")
    def test_token_and_endpoint_is_okay(self, no_client_version_check):
        Client(token="token", endpoint="https://need_an_endpoint.com")
        assert no_client_version_check.called

    def test_bad_endpoint_fails(self):
        """
        Client with bad endpoint
        """
        with mock.patch("datarobot.rest.RESTClientObject.get") as mock_version_check:
            mock_version_check.side_effect = ClientError("dummy msg", 12345)
            with pytest.raises(UserWarning, match="Server did not reply"):
                Client(token="t-token", endpoint="https://host_name.com")

    @pytest.mark.usefixtures("no_client_version_check")
    def test_re_instantiation(self):
        """
        Client re installation.
        """
        previous = Client(token="t-****", endpoint="https://end.com")
        old_client = set_client(
            RESTClientObject(auth=("u-**********", "p-******"), endpoint="https://host_name.com")
        )
        assert previous is old_client

    @pytest.mark.usefixtures("no_client_version_check")
    @responses.activate
    def test_recognizing_domain_on_instance(self):
        raw = """{"api_token": "some_token"}"""
        responses.add(
            responses.POST,
            "https://host_name.com/api/v2/api_token/",
            body=raw,
            status=201,
            content_type="application/json",
        )
        set_client(
            RESTClientObject(
                auth=("u-**********", "p-******"), endpoint="https://host_name.com/api/v2"
            )
        )
        restored_client = get_client()
        assert restored_client.domain == "https://host_name.com"

    @pytest.mark.usefixtures("no_client_version_check")
    @mock.patch("datarobot.client._file_exists", return_value=False)
    def test_instantiation_from_env(self, mock_file_exists):
        """
        Test instantiation with creds from virtual environment
        """
        with patch.dict(
            "os.environ",
            {"DATAROBOT_API_TOKEN": "venv_token", "DATAROBOT_ENDPOINT": "https://host_name.com"},
        ):
            rest_client = get_client()
            assert rest_client.token == "venv_token"
            assert rest_client.endpoint == "https://host_name.com"

        set_client(None)

        with patch.dict(
            "os.environ",
            {
                "DATAROBOT_API_TOKEN": "venv_token",
                "DATAROBOT_ENDPOINT": "https://host_name.com",
                "DATAROBOT_MAX_RETRIES": "2",
            },
        ):
            rest_client = get_client()
            assert rest_client.token == "venv_token"
            assert rest_client.connect_timeout == DEFAULT_TIMEOUT.CONNECT
            assert rest_client.adapters
            for adapter in rest_client.adapters.values():
                assert adapter.max_retries.total == 2

    @pytest.mark.usefixtures("no_client_version_check")
    @mock.patch("datarobot.client._file_exists", return_value=False)
    def test_instantiation_from_env_checks_client_compatibility(
        self, mock_file_exists, no_client_version_check
    ):
        """
        Test instantiation with creds from virtual environment checks client compatibility.
        """
        with patch.dict(
            "os.environ",
            {"DATAROBOT_API_TOKEN": "venv_token", "DATAROBOT_ENDPOINT": "https://host_name.com"},
        ):
            rest_client = Client()
            assert rest_client.token == "venv_token"
            assert rest_client.endpoint == "https://host_name.com"
        assert no_client_version_check.called

    @pytest.mark.usefixtures("no_client_version_check")
    def test_instantiation_from_file_with_wrong_path(self):
        with patch.dict("os.environ", {"DATAROBOT_CONFIG_FILE": "./tests/fixtures/.datarobotrc"}):
            with pytest.raises(ValueError):
                get_client()

    @pytest.mark.usefixtures("no_client_version_check")
    def test_instantiation_from_yaml_file_api_token(self):
        file_data = "token: fake_token\nendpoint: https://host_name.com\nmax_retries: 3"
        config_file = tempfile.NamedTemporaryFile(delete=False, suffix=".yaml")
        try:
            with open(config_file.name, mode="w") as config:
                config.write(file_data)
            fake_environ = {"DATAROBOT_CONFIG_FILE": config_file.name}
            with patch("os.environ", fake_environ):
                rest_client = get_client()
            assert rest_client.token == "fake_token"
            assert rest_client.endpoint == "https://host_name.com"
            assert rest_client.connect_timeout == DEFAULT_TIMEOUT.CONNECT
            assert rest_client.adapters
            for adapter in rest_client.adapters.values():
                assert adapter.max_retries.total == 3
        finally:
            os.remove(config_file.name)

    @pytest.mark.usefixtures("no_client_version_check")
    def test_instantiation_from_yaml_file_set_timeout(self, temporary_file):
        connect_timeout = 55
        file_data = (
            "token: fake_token\nendpoint: https://host_name.com\nconnect_timeout: {}"
        ).format(connect_timeout)
        with open(temporary_file, mode="w") as config:
            config.write(file_data)
        fake_environ = {"DATAROBOT_CONFIG_FILE": temporary_file}
        with patch("os.environ", fake_environ):
            rest_client = get_client()
        assert rest_client.connect_timeout == connect_timeout

    @pytest.mark.usefixtures("no_client_version_check")
    def test_instantiation_from_yaml_checks_client_compatibility(
        self, temporary_file, no_client_version_check
    ):
        connect_timeout = 55
        file_data = (
            "token: fake_token\nendpoint: https://host_name.com\nconnect_timeout: {}"
        ).format(connect_timeout)
        with open(temporary_file, mode="w") as config:
            config.write(file_data)
        fake_environ = {"DATAROBOT_CONFIG_FILE": temporary_file}
        with patch("os.environ", fake_environ):
            Client()
        assert no_client_version_check.called

    @pytest.mark.usefixtures("no_client_version_check")
    def test_client_from_codeline(self):
        Client(token="some_token", endpoint="https://endpoint.com")
        c = get_client()
        assert c.token == "some_token"
        assert c.endpoint == "https://endpoint.com"
        assert c.connect_timeout == DEFAULT_TIMEOUT.CONNECT
        assert c.adapters
        for adapter in c.adapters.values():
            assert adapter.max_retries.total > 0
            assert adapter.max_retries.method_whitelist == Retry.DEFAULT_METHOD_WHITELIST
            assert adapter.max_retries.respect_retry_after_header

    @pytest.mark.usefixtures("no_client_version_check")
    def test_client_from_codeline_set_timeout(self):
        connect_timeout = 55
        Client(token="some_token", endpoint="https://endpoint.com", connect_timeout=connect_timeout)
        c = get_client()
        assert c.connect_timeout == connect_timeout

    @pytest.mark.usefixtures("no_client_version_check")
    def test_client_from_codeline_max_retries(self):
        Client(
            token="some token",
            endpoint="https://endpoint.com",
            max_retries=Retry(read=3, connect=3),
        )
        c = get_client()
        assert c.adapters
        for adapter in c.adapters.values():
            assert adapter.max_retries.read == 3
            assert adapter.max_retries.connect == 3

    @pytest.mark.usefixtures("no_client_version_check")
    def test_client_user_agent(self):
        with patch("platform.system") as mock_system, patch(
            "platform.release"
        ) as mock_release, patch("platform.machine") as mock_machine, patch(
            "platform.python_version"
        ) as mock_py_version:
            mock_system.return_value = "Prince"
            mock_release.return_value = "Party"
            mock_machine.return_value = "x19_99"
            mock_py_version.return_value = "3.14.159"
            header = RESTClientObject._make_user_agent_header()
        expected_agent = "DataRobotPythonClient/{} (Prince Party x19_99) Python-3.14.159".format(
            dr.__version__
        )
        assert header == {"User-Agent": expected_agent}

    @pytest.mark.usefixtures("no_client_version_check")
    def test_client_user_agent_with_suffix(self):
        suffix = "Blamo/8.23 (6.30)"
        orig = RESTClientObject._make_user_agent_header()
        with_suffix = RESTClientObject._make_user_agent_header(suffix=suffix)
        assert with_suffix["User-Agent"].startswith(orig["User-Agent"])
        assert with_suffix["User-Agent"].endswith(" " + suffix)


class RestErrors(SDKTestcase):
    @responses.activate
    def test_404_plain_text(self):
        """
        Bad request in plain text
        """
        raw = "Not Found"

        responses.add(
            responses.GET,
            "https://host_name.com/projects/404",
            body=raw,
            status=404,
            content_type="text/plain",
        )

        client = get_client()

        with self.assertRaises(AppPlatformError) as app_error:
            client.get("projects/404")

        self.assertEqual(str(app_error.exception), "404 client error: Not Found")

    @responses.activate
    def test_404_json(self):
        """
        Bad request with datarobot reason in json
        """
        raw = """
        {"message": "Not Found"}
        """

        responses.add(
            responses.GET,
            "https://host_name.com/projects/404",
            body=raw,
            status=404,
            content_type="application/json",
        )

        client = get_client()

        with self.assertRaises(AppPlatformError) as app_error:
            client.get("projects/404")

        exception_message = str(app_error.exception)
        self.assertIn("404 client error", exception_message)
        self.assertIn("Not Found", exception_message)

    @responses.activate
    def test_500_json(self):
        """
        Bad request with datarobot reason in json
        """
        raw = """
        {"message": "Not Found"}
        """

        responses.add(
            responses.GET,
            "https://host_name.com/projects/500",
            body=raw,
            status=500,
            content_type="application/json",
        )

        client = get_client()

        with self.assertRaises(AppPlatformError) as app_error:
            client.get("projects/500")

        exception_message = str(app_error.exception)
        self.assertIn("500 server error", exception_message)
        self.assertIn("Not Found", exception_message)

    @responses.activate
    def test_other_errors(self):
        """
        Other errors
        """
        raw = """
        {"message": "Bad response"}
        """

        responses.add(
            responses.GET,
            "https://host_name.com/projects/500",
            body=raw,
            status=500,
            content_type="application/json",
        )

        client = get_client()

        with self.assertRaises(AppPlatformError) as app_error:
            client.get("projects/500")
            self.assertEqual(
                str(app_error.exception), "Connection refused: https://host_name.com/projects/500",
            )


class TestClientAttributes(unittest.TestCase):
    def test_main_useful_things_under_datarobot(self):
        """To lower the intimidation factor, let's try to limit the objects
        that show up at the root of datarobot

        This way, when they are in IPython and do tab-completion they get a
        sense for what is available to tinker with at the top level
        """
        known_names = {
            "Project",
            "Model",
            "DatetimeModel",
            "CombinedModel",
            "PrimeModel",
            "BlenderModel",
            "FrozenModel",
            "Ruleset",
            "Blueprint",
            "BlueprintTaskDocument",
            "BlueprintChart",
            "ModelBlueprintChart",
            "ModelJob",
            "PredictJob",
            "Job",
            "Predictions",
            "PredictionDataset",
            "PrimeFile",
            "QUEUE_STATUS",
            "Client",
            "AUTOPILOT_MODE",
            "AppPlatformError",
            "utils",
            "errors",
            "models",
            "client",
            "rest",
            "SCORING_TYPE",
            "DatasetFeaturelist",
            "Featurelist",
            "ModelingFeaturelist",
            "Feature",
            "FeatureHistogram",
            "FeatureSettings",
            "ModelingFeature",
            "FeatureLineage",
            "helpers",
            "RandomCV",
            "StratifiedCV",
            "GroupCV",
            "UserCV",
            "RandomTVH",
            "UserTVH",
            "StratifiedTVH",
            "GroupTVH",
            "DatetimePartitioning",
            "DatetimePartitioningSpecification",
            "BacktestSpecification",
            "partitioning_methods",
            "AdvancedOptions",
            "Periodicity",
            "VERBOSITY_LEVEL",
            "enums",
            "ImportedModel",
            "ReasonCodesInitialization",
            "ReasonCodes",
            "PayoffMatrix",
            "PredictionExplanationsInitialization",
            "PredictionExplanations",
            "RatingTable",
            "RatingTableModel",
            "TARGET_TYPE",
            "TrainingPredictions",
            "TrainingPredictionsJob",
            "ShapImpact",
            "ShapMatrix",
            "ShapMatrixJob",
            "SharingAccess",
            "ModelRecommendation",
            "DataDriver",
            "Connector",
            "DataStore",
            "Dataset",
            "DatasetDetails",
            "DatasetFeature",
            "DatasetFeatureHistogram",
            "DataSource",
            "DataSourceParameters",
            "ComplianceDocumentation",
            "ComplianceDocTemplate",
            "CalendarFile",
            "PredictionServer",
            "Deployment",
            "SecondaryDatasetConfigurations",
            "BatchPredictionJob",
            "BatchPredictionJobDefinition",
            "Credential",
            "InteractionFeature",
            "ExternalScores",
            "ExternalLiftChart",
            "ExternalResidualsChart",
            "ExternalRocCurve",
            "ExternalMulticlassLiftChart",
            "ExternalConfusionChart",
            "ExecutionEnvironment",
            "ExecutionEnvironmentVersion",
            "CustomInferenceImage",
            "CustomInferenceModel",
            "CustomModelVersion",
            "CustomModelVersionDependencyBuild",
            "CustomModelTest",
            "CustomTask",
            "CustomTaskVersion",
            "FeatureImpactJob",
            "RelationshipsConfiguration",
            "NETWORK_EGRESS_POLICY",
            "FeatureAssociationMatrix",
            "FeatureAssociationMatrixDetails",
            "FeatureAssociationFeaturelists",
            "AutomatedDocument",
            "DatasetDefinition",
            "feature_discovery",
            "SecondaryDataset",
            "SegmentationTask",
            "SegmentInfo",
            "Relationship",
            "FeatureDiscoverySetting",
            "SNAPSHOT_POLICY",
            "UserBlueprint",
            "DataEngineQueryGenerator",
            "ClassMappingAggregationSettings",
            "ClusteringModel",
            "ClusterInsight",
            "Cluster",
        }

        found_names = {name for name in dir(dr) if not name.startswith("_")}
        assert found_names == known_names


@pytest.yield_fixture
def mock_os():
    with patch("datarobot.client.os", autospec=True) as m:
        yield m


@pytest.yield_fixture
def mock_file_exists():
    with patch("datarobot.client._file_exists") as m:
        yield m


@pytest.yield_fixture
def mock_os_environ():
    with patch("datarobot.client.os.environ") as m:
        yield m
