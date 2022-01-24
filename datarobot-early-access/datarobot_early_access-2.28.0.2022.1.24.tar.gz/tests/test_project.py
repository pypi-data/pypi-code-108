# coding=utf-8
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
import datetime
import json
import os
import re

import mock
import pandas as pd
import pytest
import responses
import six

from datarobot import (
    AdvancedOptions,
    AUTOPILOT_MODE,
    Blueprint,
    ClassMappingAggregationSettings,
    errors,
    Featurelist,
    Model,
    ModelJob,
    PredictJob,
    Project,
    QUEUE_STATUS,
    RatingTable,
    RatingTableModel,
    SharingAccess,
    TARGET_TYPE,
    UserCV,
    UserTVH,
)
from datarobot.enums import PROJECT_STAGE, SCALEOUT_MODELING_MODE, UnsupervisedTypeEnum
from tests.test_helpers import fixture_file_path, URLParamsTestCase
from tests.utils import assert_raised_regex, assert_urls_equal, request_body_to_json, SDKTestcase

if six.PY3:
    from unittest.mock import patch
else:
    from mock import patch


# FIXTURES and HELPERS #############################################################################


def construct_dummy_aimed_project(
    pid="p-id", project_name="Untitled Project", target="SalePrice", autopilot_mode=0,
):
    return {
        "id": pid,
        "projectName": project_name,
        "fileName": "Untitled Project.csv",
        "stage": "modeling",
        "autopilotMode": autopilot_mode,
        "created": "2015-05-21T16:02:02.573565",
        "target": target,
        "metric": "Gamma Deviance",
        "partition": {
            "cvMethod": "random",
            "validationType": "CV",
            "validationPct": None,
            "holdoutPct": 20,
            "reps": 5,
            "holdoutLevel": None,
            "validationLevel": None,
            "trainingLevel": None,
            "partitionKeyCols": None,
            "userPartitionCol": None,
            "cvHoldoutLevel": None,
            "datetimeCol": None,
        },
        "recommender": {
            "isRecommender": False,
            "recommenderItemId": None,
            "recommenderUserId": None,
        },
        "advancedOptions": {
            "weights": None,
            "blueprintThreshold": None,
            "responseCap": False,
            "seed": None,
            "smartDownsampled": False,
            "majorityDownsamplingRate": None,
            "defaultMonotonicIncreasingFeaturelistId": None,
            "defaultMonotonicDecreasingFeaturelistId": None,
            "offset": None,
            "exposure": None,
            "allowedPairwiseInteractionGroups": [["A", "B", "C"], ["C", "D"]],
        },
        "positiveClass": None,
        "maxTrainPct": 64.0,
        "maxTrainRows": 128,
        "scaleoutMaxTrainPct": 64.0,
        "scaleoutMaxTrainRows": 128,
        "holdoutUnlocked": True,
        "targetType": "Regression",
        "unsupervisedMode": True,
    }


AIMED_PROJECT_JSON = json.dumps(construct_dummy_aimed_project())


def prep_successful_project_cloning_responses(new_name=None):
    """
    Setup the responses library to mock calls to the API necessary to
    clone a project

    Returns
    ----------
    source_pid : str
        ID of the source project to be cloned
    """
    source_project = construct_dummy_aimed_project()
    project = construct_dummy_aimed_project(
        project_name=new_name or "Copy of {}".format(source_project["projectName"]), pid="id2",
    )
    pid = project.get("id")
    responses.add(
        responses.POST,
        "https://host_name.com/projectClones/",
        body="",
        status=202,
        content_type="application/json",
        adding_headers={"Location": "https://host_name.com/status/status-id/"},
    )
    responses.add(
        responses.GET,
        "https://host_name.com/status/status-id/",
        status=303,
        body="",
        content_type="application/json",
        adding_headers={"Location": "https://host_name.com/projects/{}/".format(pid)},
    )
    responses.add(
        responses.GET,
        "https://host_name.com/projects/{}/".format(pid),
        status=200,
        body=json.dumps(project),
        content_type="application/json",
    )
    source_pid = source_project.get("id")
    responses.add(
        responses.GET,
        "https://host_name.com/projects/{}/".format(source_pid),
        status=200,
        body=json.dumps(source_project),
        content_type="application/json",
    )
    return source_pid


def prep_successful_project_creation_responses(project=None):
    """
    Setup the responses library to mock calls to the API necessary to
    create a project

    Parameters
    ----------
    project : dict
        Project JSON as a dict, as would be expected from construct_dummy_aimed_project_json
    """
    if project is None:
        project = construct_dummy_aimed_project()

    pid = project.get("id")
    responses.add(
        responses.POST,
        "https://host_name.com/projects/",
        body="",
        status=202,
        content_type="application/json",
        adding_headers={"Location": "https://host_name.com/status/status-id/"},
    )
    responses.add(
        responses.GET,
        "https://host_name.com/status/status-id/",
        status=303,
        body="",
        content_type="application/json",
        adding_headers={"Location": "https://host_name.com/projects/{}/".format(pid)},
    )
    responses.add(
        responses.GET,
        "https://host_name.com/projects/{}/".format(pid),
        status=200,
        body=json.dumps(project),
        content_type="application/json",
    )


def prep_successful_aim_responses(project=None):
    """A helper to use with setting up test scenarios where the server is
    expected to successfully set the target.

    Parameters
    ----------
    project : dict
        Project JSON as a dict, as would be expected from construct_dummy_aimed_project_json
    """
    if project is None:
        project = construct_dummy_aimed_project()

    pid = project.get("id")
    project_url = "https://host_name.com/projects/{}/".format(pid)
    aim_url = project_url + "aim/"

    responses.add(
        responses.PATCH,
        aim_url,
        body="",
        status=202,
        adding_headers={"Location": "https://host_name.com/status/some-status/"},
        content_type="application/json",
    )

    responses.add(
        responses.GET,
        "https://host_name.com/status/some-status/",
        body="",
        status=303,
        adding_headers={"Location": project_url},
        content_type="application/json",
    )
    responses.add(
        responses.GET,
        project_url,
        body=json.dumps(project),
        status=200,
        content_type="application/json",
    )


# TESTS ############################################################################################


def test_future_proof(project_with_target_data):
    Project.from_data(dict(project_with_target_data, future="new"))


@pytest.mark.usefixtures("known_warning")
def test_project_from_dict_is_deprecated(project_without_target_data):
    Project(project_without_target_data)


class ProjectTestCase(SDKTestcase):
    def setUp(self):
        self.blueprint_api_resp = [
            {
                "projectId": "p-id",
                "processes": [
                    "Regularized Linear Model Preprocessing v5",
                    "Log Transformed Response",
                ],
                "id": "cbb4d6101dea1768ed79d75edd84c6c7",
                "modelType": "Auto-tuned K-Nearest Neighbors Regressor (Minkowski Distance)",
            },
            {
                "projectId": "p-id",
                "processes": [
                    "Regularized Linear Model Preprocessing v12",
                    "Log Transformed Response",
                ],
                "id": "e0708bd47f9fd21019a5ab7846e8364d",
                "modelType": "Auto-tuned Stochastic Gradient Descent Regression",
            },
        ]

    def test_instantiation_with_data(self):
        """
        Test instantiation Project(data)
        """
        data = {
            "id": "project_id",
            "project_name": "project_test_name",
            "mode": 2,
            "stage": "stage",
            "target": "test_target",
        }
        project_inst = Project.from_data(data)
        self.assertEqual(project_inst.id, data["id"])
        self.assertEqual(project_inst.project_name, data["project_name"])
        self.assertEqual(project_inst.mode, data["mode"])
        self.assertEqual(project_inst.stage, data["stage"])
        self.assertEqual(project_inst.target, data["target"])

        self.assertEqual(repr(project_inst), "Project(project_test_name)")

    def test_print_project_nonascii_name(self):
        project = Project.from_data(
            {"id": "project-id", "project_name": u"\u3053\u3093\u306b\u3061\u306f"}
        )
        print(project)

    def test_get_permalink(self):
        p = Project("pid")
        expected = "https://host_name.com/projects/pid/models"
        self.assertEqual(expected, p.get_leaderboard_ui_permalink())

    def test_set_project_description(self):
        description = "This is my test project."
        p = Project("pid", project_description=description)
        assert p.project_description == description

    @responses.activate
    def test_update_project_description(self):
        description = "This is my test project."
        updated_description = "Project XYZ"
        responses.add(
            responses.PATCH,
            "https://host_name.com/projects/p-id/",
            body="",
            status=200,
            content_type="application/json",
        )
        p = Project("p-id", project_description=description)
        p.set_project_description(updated_description)
        assert responses.calls[0].request.method == "PATCH"
        payload = request_body_to_json(responses.calls[0].request)
        assert p.project_description == payload["projectDescription"] == updated_description

    @mock.patch("webbrowser.open")
    def test_open_leaderboard_browser(self, webbrowser_open):
        project = Project("p-id")
        project.open_leaderboard_browser()
        self.assertTrue(webbrowser_open.called)

    @responses.activate
    def test_create_project_async(self):
        prep_successful_project_creation_responses()

        new_project = Project.create(sourcedata="https://google.com")
        self.assertEqual(new_project.id, "p-id")
        self.assertEqual(new_project.project_name, "Untitled Project")

    @responses.activate
    def test_create_project_non_ascii_async(self):
        prep_successful_project_creation_responses()
        name = u"\xe3\x81\x82\xe3\x81\x82\xe3\x81\x82"
        Project.create("https://google.com", project_name=name)

    @responses.activate
    def test_get_project_metrics(self):
        """
        Test get project metrics
        """
        raw = """
        {"available_metrics":
            ["Gini Norm",
              "Weighted Gini Norm",
              "Weighted R Squared",
              "Weighted RMSLE",
              "Weighted MAPE",
              "Weighted Gamma Deviance",
              "Gamma Deviance",
              "RMSE",
              "Weighted MAD",
              "Tweedie Deviance",
              "MAD",
              "RMSLE",
              "Weighted Tweedie Deviance",
              "Weighted RMSE",
              "MAPE",
              "Weighted Poisson Deviance",
              "R Squared",
              "Poisson Deviance"],
         "feature_name": "SalePrice"}
        """
        expected_url = "https://host_name.com/projects/p-id/features/metrics/"
        responses.add(
            responses.GET, expected_url, body=raw, status=200, content_type="application/json"
        )
        get_project = Project("p-id").get_metrics("SalePrice")
        assert_urls_equal(responses.calls[0].request.url, expected_url + "?featureName=SalePrice")
        self.assertEqual(get_project["feature_name"], "SalePrice")

    @responses.activate
    def test_get_project(self):
        """
        Test get project
        """
        responses.add(
            responses.GET,
            "https://host_name.com/projects/p-id/",
            body=AIMED_PROJECT_JSON,
            status=200,
            content_type="application/json",
        )
        get_project = Project.get("p-id")
        assert get_project.id == "p-id"
        assert get_project.project_name == "Untitled Project"
        assert get_project.target == "SalePrice"
        assert get_project.target_type == "Regression"
        assert get_project.stage == "modeling"
        assert get_project.metric == "Gamma Deviance"
        assert get_project.positive_class is None
        assert get_project.max_train_pct == 64.0
        assert get_project.max_train_rows == 128
        assert get_project.scaleout_max_train_pct == 64.0
        assert get_project.scaleout_max_train_rows == 128
        assert get_project.holdout_unlocked is True
        assert get_project.unsupervised_mode is True
        assert isinstance(get_project.partition, dict)
        assert isinstance(get_project.recommender, dict)
        assert isinstance(get_project.advanced_options, dict)
        assert "weights" not in get_project.advanced_options
        assert "offset" not in get_project.advanced_options
        assert "exposure" not in get_project.advanced_options
        assert get_project.advanced_options["allowed_pairwise_interaction_groups"] == [
            ["A", "B", "C"],
            ["C", "D"],
        ]

        assert isinstance(get_project.created, datetime.datetime)

        assert get_project.partition["cv_method"] == "random"
        assert get_project.query_generator_id is None

        assert get_project.segmentation is None
        assert not get_project.is_segmented

    @responses.activate
    def test_get_segmented_parent_project(self):
        """
        Test get project
        """
        proj = construct_dummy_aimed_project()
        proj["segmentation"] = {
            "segmentationTaskId": "61c06906e6776a168debc9f0",
            "parentProjectId": None,
            "segment": None,
        }

        responses.add(
            responses.GET,
            "https://host_name.com/projects/p-id/",
            body=json.dumps(proj),
            status=200,
            content_type="application/json",
        )
        get_project = Project.get("p-id")

        assert get_project.id == "p-id"
        assert get_project.project_name == "Untitled Project"
        assert get_project.segmentation is not None
        assert get_project.is_segmented

    @responses.activate
    def test_get_segmented_child_project(self):
        """
        Test get project
        """
        proj = construct_dummy_aimed_project()
        proj["segmentation"] = {
            "segmentationTaskId": "61c06906e6776a168debc9f0",
            "parentProjectId": "61c068d5795f11f3a8821742",
            "segment": "Cluster 1",
        }

        responses.add(
            responses.GET,
            "https://host_name.com/projects/p-id/",
            body=json.dumps(proj),
            status=200,
            content_type="application/json",
        )
        get_project = Project.get("p-id")

        assert get_project.id == "p-id"
        assert get_project.project_name == "Untitled Project"
        assert get_project.segmentation is not None
        assert not get_project.is_segmented

    @responses.activate
    def test_get_monotonicity_project(self):
        mono_config = {
            "onlyIncludeMonotonicBlueprints": True,
            "defaultMonotonicDecreasingFeaturelistId": "5ae04c0d962d7410683073cb",
            "defaultMonotonicIncreasingFeaturelistId": "5ae04c0f962d7410683073cc",
        }
        project_response = construct_dummy_aimed_project()
        project_response["advancedOptions"].update(**mono_config)
        responses.add(
            responses.GET,
            "https://host_name.com/projects/p-id/",
            body=json.dumps(project_response),
            status=200,
            content_type="application/json",
        )

        get_project = Project.get("p-id")

        assert (
            get_project.advanced_options["default_monotonic_increasing_featurelist_id"]
            == mono_config["defaultMonotonicIncreasingFeaturelistId"]
        )
        assert (
            get_project.advanced_options["default_monotonic_decreasing_featurelist_id"]
            == mono_config["defaultMonotonicDecreasingFeaturelistId"]
        )
        assert (
            get_project.advanced_options["only_include_monotonic_blueprints"]
            == mono_config["onlyIncludeMonotonicBlueprints"]
        )

    @responses.activate
    def test_get_project_weights_offset_exposure(self):
        """
        Test get project with a weights, offset and exposure columns
        """
        # given a project with a weights column
        pid = "582e4309100d2b13b939b223"
        weight_var = "weight_variable"
        offset_var = ["offset_variable"]
        exposure_var = "exposure_variable"
        events_count_var = "events_count"
        project_data = construct_dummy_aimed_project()
        project_data["advancedOptions"]["weights"] = weight_var
        project_data["advancedOptions"]["offset"] = offset_var
        project_data["advancedOptions"]["exposure"] = exposure_var
        project_data["advancedOptions"]["eventsCount"] = events_count_var
        # and a mocked API GET /projects/<pid>/ response
        responses.add(
            responses.GET,
            "https://host_name.com/projects/{}/".format(pid),
            body=json.dumps(project_data),
            status=200,
            content_type="application/json",
        )

        # when method Project.get is called
        project = Project.get(pid)

        # then the resulting object contains weights in advanced options
        assert project.advanced_options["weights"] == weight_var
        assert project.advanced_options["offset"] == offset_var
        assert project.advanced_options["exposure"] == exposure_var
        assert project.advanced_options["events_count"] == events_count_var

    @responses.activate
    def test_get_feature_discovery_project(self):
        pid = "582e4309100d2b13b939b223"
        project_data = construct_dummy_aimed_project()
        project_data["useFeatureDiscovery"] = True
        responses.add(
            responses.GET,
            "https://host_name.com/projects/{}/".format(pid),
            body=json.dumps(project_data),
            status=200,
            content_type="application/json",
        )

        # when method Project.get is called
        project = Project.get(pid)
        assert project.use_feature_discovery is True

    @responses.activate
    def test_delete_project(self):
        """
        Test delete project
        """
        responses.add(responses.DELETE, "https://host_name.com/projects/p-id/", status=204)

        project = Project("p-id")
        del_result = project.delete()
        self.assertEqual(responses.calls[0].request.method, "DELETE")
        self.assertIsNone(del_result)

    @responses.activate
    def test_create_non_ascii_filename(self):
        prep_successful_project_creation_responses()
        # tests/fixtures/日本/データ.csv
        path = fixture_file_path(u"日本/データ.csv")
        Project.create(path)

        assert responses.calls[0].request.url == "https://host_name.com/projects/"
        request_message = responses.calls[0].request.body
        with open(path, "rb") as fd:
            assert fd.read() in request_message.to_string()

    @responses.activate
    def test_create_non_ascii_filepath_is_okay(self):
        """As long as the file name is ascii, we're good"""
        prep_successful_project_creation_responses()
        path = fixture_file_path(u"日本/synthetic-100.csv")

        Project.create(path)
        # decoded to str implicitly
        self.assertEqual(responses.calls[0].request.url, "https://host_name.com/projects/")
        request_message = responses.calls[0].request.body
        with open(path, "rb") as fd:
            self.assertIn(fd.read(), request_message.to_string())

    @responses.activate
    def test_clone(self):
        source_pid = prep_successful_project_cloning_responses()
        project = Project.get(source_pid)
        new_project = project.clone_project()
        assert new_project.id != project.id
        assert new_project.project_name == "Copy of {}".format(project.project_name)
        assert responses.calls[0].request.url == "https://host_name.com/projects/{}/".format(
            source_pid
        )
        assert responses.calls[1].request.url == "https://host_name.com/projectClones/"
        assert responses.calls[1].request.body == json.dumps({"projectId": source_pid}).encode(
            "utf-8"
        )
        assert responses.calls[-1].request.url == "https://host_name.com/projects/{}/".format(
            new_project.id
        )

    @responses.activate
    def test_clone_with_name(self):
        new_name = "this is my next project"
        source_pid = prep_successful_project_cloning_responses(new_name)
        project = Project.get(source_pid)
        new_project = project.clone_project(new_name)
        assert new_project.id != project.id
        assert new_project.project_name == new_name
        assert responses.calls[0].request.url == "https://host_name.com/projects/{}/".format(
            source_pid
        )
        assert responses.calls[1].request.url == "https://host_name.com/projectClones/"
        assert responses.calls[1].request.body == json.dumps(
            {"projectId": source_pid, "projectName": new_name}
        ).encode("utf-8")
        assert responses.calls[-1].request.url == "https://host_name.com/projects/{}/".format(
            new_project.id
        )

    @responses.activate
    def test_rename(self):
        responses.add(
            responses.PATCH,
            "https://host_name.com/projects/p-id/",
            body="",
            status=200,
            content_type="application/json",
        )
        project = Project("p-id")
        project.rename("new name")
        assert responses.calls[0].request.method == "PATCH"
        payload = request_body_to_json(responses.calls[0].request)
        assert project.project_name == payload["projectName"] == "new name"

    @responses.activate
    def test_unlock_holdout(self):
        responses.add(
            responses.PATCH,
            "https://host_name.com/projects/p-id/",
            body="",
            status=200,
            content_type="application/json",
        )
        project = Project("p-id")
        upd_data = project.unlock_holdout()
        self.assertEqual(responses.calls[0].request.method, "PATCH")
        payload = request_body_to_json(responses.calls[0].request)
        self.assertTrue(payload["holdoutUnlocked"])
        self.assertTrue(upd_data)

    @responses.activate
    def test_set_worker_count(self):
        responses.add(
            responses.PATCH,
            "https://host_name.com/projects/p-id/",
            body="",
            status=200,
            content_type="application/json",
        )
        project = Project("p-id")
        project.set_worker_count(20)
        self.assertEqual(responses.calls[0].request.method, "PATCH")
        payload = request_body_to_json(responses.calls[0].request)
        self.assertTrue(payload["workerCount"])

    @responses.activate
    def test_project_create_uses_read_timeout(self):
        """
        Check that the read_timeout parameter gets passed correctly down into
        the `requests` library

        The 400 is just because it's a simple way to short-circuit out of the project
        creation flow, which uses 3 total requests.
        """
        path = fixture_file_path("synthetic-100.csv")

        responses.add(responses.POST, "https://host_name.com/projects/", body="", status=400)
        with mock.patch.object(
            Project._client, "request", wraps=Project._client.request
        ) as mock_request:
            try:
                Project.create(path, read_timeout=2)
            except errors.ClientError:
                pass

            timeout = mock_request.call_args[1]["timeout"]
            assert timeout[0] == 6.05  # Connect timeout; specified in RESTClientObject
            assert timeout[1] == 2  # Read timeout; specified in the function call

    @responses.activate
    def test_by_upload_file_path(self):
        """
        Project.create(
            'synthetic-100.csv')
        """
        prep_successful_project_creation_responses()
        path = fixture_file_path("synthetic-100.csv")

        Project.create(path)
        # decoded to str implicitly
        self.assertEqual(responses.calls[0].request.url, "https://host_name.com/projects/")
        request_message = responses.calls[0].request.body
        with open(path, "rb") as fd:
            self.assertIn(fd.read(), request_message.to_string())

    def test_by_upload_file_path_fail(self):
        """
        Bad file name: Project.create('meh.csv')
        """
        path = fixture_file_path("does_not_exist.csv")
        with self.assertRaises(errors.InputNotUnderstoodError):
            Project.create(path)

    @responses.activate
    def test_by_upload_file_content(self):
        """
        Project.create(b'lalalala')
        """
        prep_successful_project_creation_responses()

        content_line = six.b("one,two\n" + "1,2" * 100)
        Project.create(content_line)
        # decoded to str implicitly
        request_message = responses.calls[0].request.body
        self.assertIn(content_line, request_message.to_string())

    @responses.activate
    def test_project_create_filename(self):
        """
        Project.create(b'lalalala', dataset_filename='my test dataset')
        """
        prep_successful_project_creation_responses()

        content_line = six.b("one,two\n" + "1,2" * 100)
        dataset_filename = "my test dataset"
        Project.create(content_line, dataset_filename=dataset_filename)

        fields = responses.calls[0].request.body.fields
        # Test that the provided dataset_filename was used in the request to api
        assert "file" in fields
        assert fields["file"][0] == dataset_filename

    @responses.activate
    def test_by_upload_file_path_pathlib(self):
        """
        Project.create(Path('synthetic-100.csv'))
        We will use `DummyPathObject` class as a sample of pathlib.Path object,
        as pathlib.Path is not supported for python lower than 3.4 without having extra dependency.
        """

        class DummyPathObject:
            def __init__(self, path):
                self.path = path

            def __str__(self):
                return str(self.path)

        prep_successful_project_creation_responses()
        path_str = fixture_file_path("synthetic-100.csv")
        path_obj = DummyPathObject(path_str)
        Project.create(path_obj)
        # decoded to str implicitly
        self.assertEqual(responses.calls[0].request.url, "https://host_name.com/projects/")
        request_message = responses.calls[0].request.body
        with open(path_str, "rb") as fd:
            self.assertIn(fd.read(), request_message.to_string())

    @responses.activate
    def test_by_upload_file_path_pathlib_invalid(self):
        """
        Bad file name: Project.create(Path('meh.csv'))
        We will use `DummyPathObject` class as a sample of pathlib.Path object,
        as pathlib.Path is not supported for python lower than 3.4 without having extra dependency.
        """

        class DummyPathObject:
            def __init__(self, path):
                self.path = path

            def __str__(self):
                return str(self.path)

        path_str = fixture_file_path("does_not_exist.csv")
        path_obj = DummyPathObject(path_str)
        with self.assertRaises(errors.InputNotUnderstoodError):
            Project.create(path_obj)

    def test_by_upload_content_encoding(self):
        """
        Bad content encoding Project.create(u'lalalala')
        """
        content_line = u"lalalala"
        with self.assertRaises(errors.InputNotUnderstoodError):
            Project.create(content_line)

    @responses.activate
    def test_by_upload_from_fd(self):
        """
        Project.create(
          sourcedata=open('synthetic-100.csv'))
        """
        prep_successful_project_creation_responses()

        path = fixture_file_path("synthetic-100.csv")

        with open(path, "rb") as fd:
            Project.create(sourcedata=fd)
            request_message = responses.calls[0].request.body

            with open(path, "rb") as fd2:
                self.assertIn(fd2.read(), request_message.to_string())

        file_like = six.StringIO("thra\ntata\nrata")
        Project.create(sourcedata=file_like)

        # decoded to str implicitly
        request_message = responses.calls[3].request.body
        self.assertIn(six.b("thra\ntata\nrata"), request_message.to_string())

    @responses.activate
    def test_by_upload_file_seek(self):
        """
        Seek to EOF Project.create(
            open('synthetic-100.csv')
        """
        prep_successful_project_creation_responses()

        path = fixture_file_path("synthetic-100.csv")
        with open(path, "rb") as fd:
            fd.seek(20000000)
            Project.create(fd)
            # decoded to str implicitly

            request_message = responses.calls[0].request.body
            with open(path, "rb") as fd2:
                self.assertIn(fd2.read(), request_message.to_string())

    @responses.activate
    def test_by_upload_file_closed(self):
        """
        Closed fd Project.create(
            open('synthetic-100.csv')
        """
        path = fixture_file_path("synthetic-100.csv")
        responses.add(
            responses.POST, "https://host_name.com/projects/p-id/upload/", body="", status=200,
        )
        fd = open(path)
        fd.close()
        with self.assertRaises(ValueError):
            Project.create(fd)

    @responses.activate
    def test_upload_by_file_url(self):
        """
        Project.create('http:/google.com/datarobot.csv')
        """
        prep_successful_project_creation_responses()

        link = "http:/google.com/datarobot.csv"
        Project.create(sourcedata=link)
        request_message = request_body_to_json(responses.calls[0].request)
        assert request_message == {
            "url": link,
            "projectName": "Untitled Project",
        }
        self.assertEqual(responses.calls[0].request.url, "https://host_name.com/projects/")

    @responses.activate
    def test_set_target(self):
        """
        Project('project-id').set_target('SalePrice', metric='RMSE')
        """
        prep_successful_aim_responses()
        opts = AdvancedOptions(
            weights="WeightName",
            offset=["OffsetName1", "OffsetName2"],
            events_count="events_count_col",
            exposure="ExposureName",
            allowed_pairwise_interaction_groups=[["A", "B", "C"], ["C", "D"]],
        )
        upd_project = Project("p-id").set_target(
            "SalePrice", mode=AUTOPILOT_MODE.FULL_AUTO, metric="RMSE", advanced_options=opts
        )

        request_message = request_body_to_json(responses.calls[0].request)
        assert request_message == {
            "target": "SalePrice",
            "mode": AUTOPILOT_MODE.FULL_AUTO,
            "metric": "RMSE",
            "weights": "WeightName",
            "offset": ["OffsetName1", "OffsetName2"],
            "exposure": "ExposureName",
            "eventsCount": "events_count_col",
            "smartDownsampled": False,
            "allowedPairwiseInteractionGroups": [["A", "B", "C"], ["C", "D"]],
            "quickrun": False,
            "autopilotWithFeatureDiscovery": False,
            "featureDiscoverySupervisedFeatureReduction": True,
        }
        self.assertEqual(responses.calls[0].request.method, "PATCH")
        self.assertEqual(responses.calls[1].request.method, "GET")
        self.assertIsInstance(upd_project, Project)
        advanced = upd_project.advanced_options
        assert advanced["response_cap"] is False
        assert advanced["smart_downsampled"] is False

    @responses.activate
    def test_set_target_price(self):
        """
        Project('project-id').set_target('SalePrice', metric='RMSE')
        """
        prep_successful_aim_responses()
        upd_project = Project("p-id").set_target("SalePrice")

        request_message = request_body_to_json(responses.calls[0].request)
        assert request_message == {
            "target": "SalePrice",
            "mode": AUTOPILOT_MODE.FULL_AUTO,
            "quickrun": True,
        }
        self.assertEqual(upd_project.metric, "Gamma Deviance")

    @responses.activate
    def test_set_target_quickrun_mode(self):
        prep_successful_aim_responses()
        Project("p-id").set_target("SalePrice", mode=AUTOPILOT_MODE.QUICK)

        request_body = request_body_to_json(responses.calls[0].request)
        assert request_body["mode"] == AUTOPILOT_MODE.FULL_AUTO
        assert request_body["quickrun"] is True

    @responses.activate
    def test_set_target_with_valid_target_type_binary(self):
        valid_target_type = TARGET_TYPE.BINARY
        prep_successful_aim_responses()
        Project("p-id").set_target("SalePrice", target_type=valid_target_type)

        request_body = request_body_to_json(responses.calls[0].request)
        assert request_body["targetType"] == valid_target_type

    @responses.activate
    def test_set_target_with_valid_target_type_regression(self):
        valid_target_type = TARGET_TYPE.REGRESSION
        prep_successful_aim_responses()
        Project("p-id").set_target("SalePrice", target_type=valid_target_type)

        request_body = request_body_to_json(responses.calls[0].request)
        assert request_body["targetType"] == valid_target_type

    @responses.activate
    def test_set_target_with_valid_target_type_multiclass(self):
        valid_target_type = TARGET_TYPE.MULTICLASS
        prep_successful_aim_responses()
        Project("p-id").set_target("SalePrice", target_type=valid_target_type)

        request_body = request_body_to_json(responses.calls[0].request)
        assert request_body["targetType"] == valid_target_type

    @responses.activate
    def test_set_target_with_valid_target_type_multilabel(self):
        valid_target_type = TARGET_TYPE.MULTILABEL
        prep_successful_aim_responses()
        Project("p-id").set_target("SalePrice", target_type=valid_target_type)

        request_body = request_body_to_json(responses.calls[0].request)
        assert request_body["targetType"] == valid_target_type

    @responses.activate
    def test_set_target_with_invalid_target_type(self):
        invalid_target_type = "blackbox_magic"
        prep_successful_aim_responses()

        with pytest.raises(TypeError) as exc_info:
            Project("p-id").set_target("SalePrice", target_type=invalid_target_type)
        assert_raised_regex(exc_info, "is not a valid target_type")

        # Make sure that we did not actually make an invalid API call
        assert len(responses.calls) == 0

    @responses.activate
    def test_set_target_async_error(self):
        """
        Project('project-id').set_target('SalePrice', metric='RMSE')
        """
        responses.add(
            responses.PATCH,
            "https://host_name.com/projects/p-id/aim/",
            body="",
            status=202,
            adding_headers={"Location": "https://host_name.com/projects/p-id/"},
            content_type="application/json",
        )

        responses.add(
            responses.GET,
            "https://host_name.com/projects/p-id/",
            body=json.dumps({"status": "ERROR"}),
            status=200,
            content_type="application/json",
        )
        with self.assertRaises(errors.AsyncProcessUnsuccessfulError):
            Project("p-id").set_target(
                "SalePrice", metric="RMSE",
            )
        self.assertEqual(responses.calls[0].request.method, "PATCH")
        self.assertEqual(responses.calls[1].request.method, "GET")

    def test_advanced_options_must_be_object(self):
        with self.assertRaises(TypeError):
            Project("p-id").set_target("SalePrice", advanced_options={"garbage": "in"})

    @responses.activate
    def test_set_blueprint_threshold(self):
        """
        Set blueprint threshold
        """
        prep_successful_aim_responses()

        opts = AdvancedOptions(blueprint_threshold=2)
        upd_project = Project("p-id").set_target("SalePrice", advanced_options=opts)

        request_body = request_body_to_json(responses.calls[0].request)
        assert request_body == {
            "target": "SalePrice",
            "mode": AUTOPILOT_MODE.FULL_AUTO,
            "autopilotWithFeatureDiscovery": False,
            "featureDiscoverySupervisedFeatureReduction": True,
            "blueprintThreshold": 2,
            "smartDownsampled": False,
            "quickrun": True,
        }
        self.assertEqual(responses.calls[0].request.method, "PATCH")
        self.assertEqual(responses.calls[1].request.method, "GET")
        self.assertIsInstance(upd_project, Project)

    @responses.activate
    def test_blend_best_models_in_payload(self):
        prep_successful_aim_responses()

        opts = AdvancedOptions(blend_best_models=True)
        Project("p-id").set_target("SalePrice", advanced_options=opts)

        request_body = request_body_to_json(responses.calls[0].request)
        assert request_body["blendBestModels"] is True

    @responses.activate
    def test_set_blend_best_models_unset_not_in_payload(self):
        prep_successful_aim_responses()

        opts = AdvancedOptions()
        Project("p-id").set_target("SalePrice", advanced_options=opts)

        request_body = request_body_to_json(responses.calls[0].request)
        assert "blendBestModels" not in request_body

    @responses.activate
    def test_scoring_code_only_in_payload(self):
        prep_successful_aim_responses()

        opts = AdvancedOptions(scoring_code_only=True)
        Project("p-id").set_target("SalePrice", advanced_options=opts)

        request_body = request_body_to_json(responses.calls[0].request)
        assert request_body["scoringCodeOnly"] is True

    @responses.activate
    def test_set_scoring_code_only_unset_not_in_payload(self):
        prep_successful_aim_responses()

        opts = AdvancedOptions()
        Project("p-id").set_target("SalePrice", advanced_options=opts)

        request_body = request_body_to_json(responses.calls[0].request)
        assert "scoringCodeOnly" not in request_body

    @responses.activate
    def test_set_shap_only_mode_in_payload(self):
        prep_successful_aim_responses()

        opts = AdvancedOptions(shap_only_mode=True)
        Project("p-id").set_target("SalePrice", advanced_options=opts)

        request_body = request_body_to_json(responses.calls[0].request)
        assert request_body["shapOnlyMode"] is True

    @responses.activate
    def test_set_shap_only_mode_unset_not_in_payload(self):
        prep_successful_aim_responses()

        opts = AdvancedOptions()
        Project("p-id").set_target("SalePrice", advanced_options=opts)

        request_body = request_body_to_json(responses.calls[0].request)
        assert "shapOnlyMode" not in request_body

    @responses.activate
    def test_prepare_model_for_deployment_in_payload(self):
        prep_successful_aim_responses()

        opts = AdvancedOptions(prepare_model_for_deployment=True)
        Project("p-id").set_target("SalePrice", advanced_options=opts)

        request_body = request_body_to_json(responses.calls[0].request)
        assert request_body["prepareModelForDeployment"] is True

    @responses.activate
    def test_set_prepare_model_for_deployment_unset_not_in_payload(self):
        prep_successful_aim_responses()

        opts = AdvancedOptions()
        Project("p-id").set_target("SalePrice", advanced_options=opts)

        request_body = request_body_to_json(responses.calls[0].request)
        assert "prepareModelForDeployment" not in request_body

    @responses.activate
    def test_consider_blenders_in_recommendation_in_payload(self):
        prep_successful_aim_responses()

        opts = AdvancedOptions(consider_blenders_in_recommendation=True)
        Project("p-id").set_target("SalePrice", advanced_options=opts)

        request_body = request_body_to_json(responses.calls[0].request)
        assert request_body["considerBlendersInRecommendation"] is True

    @responses.activate
    def test_set_consider_blenders_in_recommendation_unset_not_in_payload(self):
        prep_successful_aim_responses()

        opts = AdvancedOptions()
        Project("p-id").set_target("SalePrice", advanced_options=opts)

        request_body = request_body_to_json(responses.calls[0].request)
        assert "considerBlendersInRecommendation" not in request_body

    @responses.activate
    def test_min_secondary_validation_model_count_in_payload(self):
        prep_successful_aim_responses()

        opts = AdvancedOptions(min_secondary_validation_model_count=5)
        Project("p-id").set_target("SalePrice", advanced_options=opts)

        request_body = request_body_to_json(responses.calls[0].request)
        assert request_body["minSecondaryValidationModelCount"] == 5

    @responses.activate
    def test_set_min_secondary_validation_model_count_unset_not_in_payload(self):
        prep_successful_aim_responses()

        opts = AdvancedOptions()
        Project("p-id").set_target("SalePrice", advanced_options=opts)

        request_body = request_body_to_json(responses.calls[0].request)
        assert "prepareModelForDeployment" not in request_body

    @responses.activate
    def test_set_response_cap(self):
        """
        Set Response Cap
        """
        prep_successful_aim_responses()

        opts = AdvancedOptions(response_cap=0.7)
        upd_project = Project("p-id").set_target("SalePrice", advanced_options=opts)

        request_body = request_body_to_json(responses.calls[0].request)
        assert request_body == {
            "target": "SalePrice",
            "mode": AUTOPILOT_MODE.FULL_AUTO,
            "responseCap": 0.7,
            "smartDownsampled": False,
            "quickrun": True,
            "autopilotWithFeatureDiscovery": False,
            "featureDiscoverySupervisedFeatureReduction": True,
        }
        self.assertEqual(responses.calls[0].request.method, "PATCH")
        self.assertEqual(responses.calls[1].request.method, "GET")
        self.assertIsInstance(upd_project, Project)

    @responses.activate
    def test_set_seed(self):
        """
        Set Response Cap
        """
        prep_successful_aim_responses()

        opts = AdvancedOptions(seed=22)
        upd_project = Project("p-id").set_target("SalePrice", advanced_options=opts)

        request_body = request_body_to_json(responses.calls[0].request)
        assert request_body == {
            "target": "SalePrice",
            "mode": AUTOPILOT_MODE.FULL_AUTO,
            "seed": 22,
            "smartDownsampled": False,
            "quickrun": True,
            "autopilotWithFeatureDiscovery": False,
            "featureDiscoverySupervisedFeatureReduction": True,
        }
        self.assertEqual(responses.calls[0].request.method, "PATCH")
        self.assertEqual(responses.calls[1].request.method, "GET")
        self.assertIsInstance(upd_project, Project)

    @responses.activate
    def test_set_smart_sampled(self):
        prep_successful_aim_responses()

        opts = AdvancedOptions(smart_downsampled=True, majority_downsampling_rate=50.5)
        upd_project = Project("p-id").set_target("SalePrice", advanced_options=opts)

        request_body = request_body_to_json(responses.calls[0].request)
        assert request_body == {
            "target": "SalePrice",
            "mode": AUTOPILOT_MODE.FULL_AUTO,
            "smartDownsampled": True,
            "majorityDownsamplingRate": 50.5,
            "quickrun": True,
            "autopilotWithFeatureDiscovery": False,
            "featureDiscoverySupervisedFeatureReduction": True,
        }
        assert isinstance(upd_project, Project)

    @responses.activate
    def test_set_datetime_autopilot_data_sampling_method(self):
        prep_successful_aim_responses()

        opts = AdvancedOptions(autopilot_data_sampling_method="latest")
        upd_project = Project("p-id").set_target("SalePrice", advanced_options=opts)

        request_body = request_body_to_json(responses.calls[0].request)
        assert request_body == {
            "target": "SalePrice",
            "mode": AUTOPILOT_MODE.FULL_AUTO,
            "smartDownsampled": False,
            "autopilotWithFeatureDiscovery": False,
            "featureDiscoverySupervisedFeatureReduction": True,
            "autopilotDataSamplingMethod": "latest",
            "quickrun": True,
        }
        assert isinstance(upd_project, Project)

    @responses.activate
    def test_set_run_leakage_removed_feature_list(self):
        """
        Set project with run leakage removed feature list option
        """
        prep_successful_aim_responses()

        opts = AdvancedOptions(run_leakage_removed_feature_list=False)
        Project("p-id").set_target("SalePrice", advanced_options=opts)

        request_body = request_body_to_json(responses.calls[0].request)
        assert request_body["runLeakageRemovedFeatureList"] is False

    @responses.activate
    def test_set_autopilot_with_feature_discovery(self):
        """Set project to run feature discovery"""
        prep_successful_aim_responses()

        opts = AdvancedOptions(autopilot_with_feature_discovery=True)
        upd_project = Project("p-id").set_target("SalePrice", advanced_options=opts)

        request_body = request_body_to_json(responses.calls[0].request)
        assert request_body == {
            "target": "SalePrice",
            "mode": AUTOPILOT_MODE.FULL_AUTO,
            "autopilotWithFeatureDiscovery": True,
            "featureDiscoverySupervisedFeatureReduction": True,
            "smartDownsampled": False,
            "quickrun": True,
        }
        self.assertEqual(responses.calls[0].request.method, "PATCH")
        self.assertEqual(responses.calls[1].request.method, "GET")
        self.assertIsInstance(upd_project, Project)

    @responses.activate
    def test_set_feature_discovery_supervised_feature_reduction(self):
        """Set project to run feature discovery superwised feature reduction"""
        prep_successful_aim_responses()

        opts = AdvancedOptions(feature_discovery_supervised_feature_reduction=True)
        upd_project = Project("p-id").set_target("SalePrice", advanced_options=opts)

        request_body = request_body_to_json(responses.calls[0].request)
        assert request_body == {
            "target": "SalePrice",
            "mode": AUTOPILOT_MODE.FULL_AUTO,
            "autopilotWithFeatureDiscovery": False,
            "featureDiscoverySupervisedFeatureReduction": True,
            "smartDownsampled": False,
            "quickrun": True,
        }
        self.assertEqual(responses.calls[0].request.method, "PATCH")
        self.assertEqual(responses.calls[1].request.method, "GET")
        self.assertIsInstance(upd_project, Project)

    @responses.activate
    def test_set_target_advance_partition_method_cv(self):
        """
        Set project with advanced partition method
        """
        prep_successful_aim_responses()

        part_method = UserCV(user_partition_col="NumPartitions", cv_holdout_level=1, seed=42)
        p = Project("p-id").set_target("SalePrice", partitioning_method=part_method)
        request_body = request_body_to_json(responses.calls[0].request)
        assert request_body == {
            "target": "SalePrice",
            "mode": AUTOPILOT_MODE.FULL_AUTO,
            "userPartitionCol": "NumPartitions",
            "cvHoldoutLevel": 1,
            "seed": 42,
            "validationType": "CV",
            "cvMethod": "user",
            "quickrun": True,
        }
        self.assertEqual(responses.calls[0].request.method, "PATCH")
        self.assertEqual(responses.calls[1].request.method, "GET")
        self.assertIsInstance(p, Project)

    @responses.activate
    def test_set_target_advance_partition_method_tvh(self):
        """
        Set project with advanced partition method
        """
        prep_successful_aim_responses()
        part_method = UserTVH(
            user_partition_col="NumPartitions",
            validation_level=1,
            training_level=2,
            holdout_level=3,
            seed=42,
        )
        p = Project("p-id").set_target("SalePrice", partitioning_method=part_method)

        request_body = request_body_to_json(responses.calls[0].request)
        assert request_body == {
            "target": "SalePrice",
            "mode": AUTOPILOT_MODE.FULL_AUTO,
            "userPartitionCol": "NumPartitions",
            "holdoutLevel": 3,
            "seed": 42,
            "validationLevel": 1,
            "trainingLevel": 2,
            "validationType": "TVH",
            "cvMethod": "user",
            "quickrun": True,
        }
        self.assertEqual(responses.calls[0].request.method, "PATCH")
        self.assertEqual(responses.calls[1].request.method, "GET")
        self.assertIsInstance(p, Project)

    @responses.activate
    def test_set_target_specify_positive_class(self):
        """
        Set project with advanced partition method
        """
        prep_successful_aim_responses()

        p = Project("p-id").set_target("Forks", positive_class="None or Unspecified")
        request_body = request_body_to_json(responses.calls[0].request)
        assert request_body == {
            "target": "Forks",
            "positiveClass": "None or Unspecified",
            "mode": AUTOPILOT_MODE.FULL_AUTO,
            "quickrun": True,
        }
        self.assertEqual(responses.calls[0].request.method, "PATCH")
        self.assertEqual(responses.calls[1].request.method, "GET")
        self.assertIsInstance(p, Project)

    @responses.activate
    @pytest.mark.usefixtures("known_warning")
    def test_set_target_quickrun_param(self):
        """
        Set project with quickrun option
        """
        prep_successful_aim_responses()

        p = Project("p-id").set_target("Forks", mode=AUTOPILOT_MODE.MANUAL, quickrun=True)
        request_body = request_body_to_json(responses.calls[0].request)
        assert request_body == {
            "target": "Forks",
            "quickrun": True,
            "mode": AUTOPILOT_MODE.FULL_AUTO,
        }
        self.assertEqual(responses.calls[0].request.method, "PATCH")
        self.assertEqual(responses.calls[1].request.method, "GET")
        self.assertIsInstance(p, Project)

    @responses.activate
    def test_set_target_comprehensive(self):
        """
        Set project in comprehensive Autopilot
        """
        prep_successful_aim_responses()

        p = Project("p-id").set_target("Forks", mode=AUTOPILOT_MODE.COMPREHENSIVE)
        request_body = request_body_to_json(responses.calls[0].request)
        assert request_body == {"target": "Forks", "mode": AUTOPILOT_MODE.COMPREHENSIVE}
        self.assertEqual(responses.calls[0].request.method, "PATCH")
        self.assertEqual(responses.calls[1].request.method, "GET")
        self.assertIsInstance(p, Project)

    def test_pass_advance_part_wrong(self):
        with self.assertRaises(TypeError):
            Project("p-id").set_target("SalePrice", partitioning_method={"CV": "TVH"})

    @responses.activate
    def test_set_target_relationships_configuration_id_n_credentials(self):
        relationships_configuration_id = "config-id"
        credentials = [
            {"user": "abc", "password": "qwerty", "catalog_version_id": "v-id", "url": "abc.jsbc"},
            {"credential_id": "cd_r", "catalog_version_id": "v-id", "url": "erf.sql"},
        ]
        project = {
            "id": "p-id",
            "target": "SalePrice",
            "fileName": "Untitled Project.csv",
            "stage": "modeling",
            "relationshipsConfigurationId": relationships_configuration_id,
            "credentials": credentials,
        }
        prep_successful_aim_responses(project=project)

        project = Project("p-id").set_target(
            target="SalePrice",
            relationships_configuration_id=relationships_configuration_id,
            credentials=credentials,
        )

        request_message = request_body_to_json(responses.calls[0].request)
        assert request_message == {
            "target": "SalePrice",
            "mode": AUTOPILOT_MODE.FULL_AUTO,
            "quickrun": True,
            "relationshipsConfigurationId": "config-id",
            "credentials": [
                {
                    "user": "abc",
                    "password": "qwerty",
                    "catalogVersionId": "v-id",
                    "url": "abc.jsbc",
                },
                {"credentialId": "cd_r", "catalogVersionId": "v-id", "url": "erf.sql"},
            ],
        }
        self.assertIsInstance(project, Project)
        self.assertEqual(project.relationships_configuration_id, relationships_configuration_id)
        self.assertEqual(project.credentials, credentials)

    @responses.activate
    def test_pause_autopilot(self):
        """
        Project('project-id').pause_autopilot()
        """
        responses.add(
            responses.POST,
            "https://host_name.com/projects/p-id/autopilot/",
            body="",
            status=202,
            content_type="application/json",
        )
        self.assertTrue(Project("p-id").pause_autopilot())
        request_body = request_body_to_json(responses.calls[0].request)
        assert request_body == {"command": "stop"}

    @responses.activate
    def test_unpause_autopilot(self):
        """
        Project('project-id').unpause_autopilot()
        """
        responses.add(
            responses.POST,
            "https://host_name.com/projects/p-id/autopilot/",
            body="",
            status=202,
            content_type="application/json",
        )
        self.assertTrue(Project("p-id").unpause_autopilot())
        request_body = request_body_to_json(responses.calls[0].request)
        assert request_body == {"command": "start"}

    @responses.activate
    def test_get_featurelists(self):
        """project.get_featurelists()"""
        some_featurelists = [
            {
                "id": "f-id-1",
                "projectId": "p-id",
                "name": "Raw Features",
                "features": ["One Fish", "Two Fish", "Red Fish", "Blue Fish"],
            },
            {
                "id": "f-id-2",
                "projectId": "p-id",
                "name": "Informative Features",
                "features": ["One Fish", "Red Fish", "Blue Fish"],
            },
            {
                "id": "f-id-3",
                "projectId": "p-id",
                "name": "Custom Features",
                "features": ["One Fish", "Blue Fish"],
            },
        ]

        responses.add(
            responses.GET,
            "https://host_name.com/projects/p-id/featurelists/",
            body=json.dumps(some_featurelists),
            status=200,
            content_type="application/json",
        )
        flists = Project("p-id").get_featurelists()
        for flist in flists:
            self.assertIsInstance(flist, Featurelist)

    def test_create_featurelist_duplicate_features(self):
        project = Project("p-id")
        with pytest.raises(errors.DuplicateFeaturesError) as exc_info:
            project.create_featurelist("test", ["feature", "feature"])
        assert_raised_regex(exc_info, "Can't create featurelist with duplicate features")

    @responses.activate
    def test_start_project(self):
        """
        Project.start("test_name",
                      "file.csv",
                      "a_target",
                      worker_count=4,
                      metric="a_metric")
        """
        path = fixture_file_path("synthetic-100.csv")
        prep_successful_project_creation_responses()

        responses.add(
            responses.PATCH,
            "https://host_name.com/projects/p-id/",
            body="",
            status=200,
            content_type="application/json",
        )

        prep_successful_aim_responses()

        proj = Project.start(
            project_name="test_name",
            sourcedata=path,
            target="a_target",
            worker_count=4,
            metric="a_metric",
        )
        self.assert_project_start_call_order()
        self.assertIsInstance(proj, Project)

    @responses.activate
    def test_start_project_from_dataframe(self):
        """
        Project.start("test_name",
                      "file.csv",
                      "a_target",
                      worker_count=4,
                      metric="a_metric")
        """
        prep_successful_project_creation_responses()

        responses.add(
            responses.PATCH,
            "https://host_name.com/projects/p-id/",
            body="",
            status=200,
            content_type="application/json",
        )

        prep_successful_aim_responses()

        dataframe = pd.DataFrame({"a_target": range(100), "predictor": range(100, 200)})
        proj = Project.start(dataframe, "a_target", "test_name", worker_count=4, metric="a_metric")
        self.assert_project_start_call_order()
        self.assertIsInstance(proj, Project)

    @responses.activate
    def test_start_project_in_manual_mode(self):
        """
        Project.start("test_name",
                      "file.csv",
                      "a_target",
                      worker_count=4,
                      metric="a_metric",
                      autopilot_on=False)
        """
        path = fixture_file_path("synthetic-100.csv")
        prep_successful_project_creation_responses()
        responses.add(
            responses.PATCH,
            "https://host_name.com/projects/p-id/",
            body="",
            status=200,
            content_type="application/json",
        )
        prep_successful_aim_responses()

        proj = Project.start(
            path, "test_name", "a_target", worker_count=4, metric="a_metric", autopilot_on=False
        )
        self.assert_project_start_call_order()
        self.assertIsInstance(proj, Project)

        request_body = request_body_to_json(responses.calls[4].request)
        self.assertEqual(request_body["mode"], AUTOPILOT_MODE.MANUAL)

    @responses.activate
    def test_start_feature_discovery_project(self):
        path = fixture_file_path("synthetic-100.csv")
        prep_successful_project_creation_responses()

        responses.add(
            responses.PATCH,
            "https://host_name.com/projects/p-id/",
            body="",
            status=200,
            content_type="application/json",
        )

        prep_successful_aim_responses()

        proj = Project.start(
            project_name="test_name",
            sourcedata=path,
            target="a_target",
            worker_count=4,
            metric="a_metric",
            relationships_configuration_id="r-id",
        )
        self.assert_project_start_call_order()
        self.assertIsInstance(proj, Project)

        request_body = request_body_to_json(responses.calls[4].request)
        self.assertEqual(request_body["relationshipsConfigurationId"], "r-id")

    @responses.activate
    def test_set_scaleout_mode(self):
        """
        Project('project-id').set_target('SalePrice', metric='RMSE')
        """
        prep_successful_aim_responses()
        opts = AdvancedOptions(scaleout_modeling_mode=SCALEOUT_MODELING_MODE.AUTOPILOT)
        upd_project = Project("p-id").set_target("SalePrice", metric="RMSE", advanced_options=opts)

        request_body = request_body_to_json(responses.calls[0].request)
        self.assertEqual(
            request_body,
            {
                "target": "SalePrice",
                "mode": AUTOPILOT_MODE.FULL_AUTO,
                "metric": "RMSE",
                "smartDownsampled": False,
                "scaleoutModelingMode": SCALEOUT_MODELING_MODE.AUTOPILOT,
                "quickrun": True,
                "autopilotWithFeatureDiscovery": False,
                "featureDiscoverySupervisedFeatureReduction": True,
            },
        )
        self.assertEqual(responses.calls[0].request.method, "PATCH")
        self.assertEqual(responses.calls[1].request.method, "GET")
        self.assertIsInstance(upd_project, Project)

    def assert_project_start_call_order(self):
        """Run this assertion to assert that the expected calls for project.start
        happened, and in the correct order

        This is a terribly brittle test. If we can come up with something
        better, let's go with that.
        """
        # Create Project
        self.assertEqual(responses.calls[0].request.url, "https://host_name.com/projects/")
        self.assertEqual(responses.calls[0].request.method, "POST")

        # Get Project Creation Status
        self.assertEqual(responses.calls[1].request.url, "https://host_name.com/status/status-id/")
        self.assertEqual(responses.calls[1].request.method, "GET")

        # Get Created Project
        self.assertEqual(responses.calls[2].request.url, "https://host_name.com/projects/p-id/")
        self.assertEqual(responses.calls[2].request.method, "GET")

        # Set Worker Count
        self.assertEqual(responses.calls[3].request.url, "https://host_name.com/projects/p-id/")
        self.assertEqual(responses.calls[3].request.method, "PATCH")

        # Set Target
        self.assertEqual(responses.calls[4].request.url, "https://host_name.com/projects/p-id/aim/")
        self.assertEqual(responses.calls[4].request.method, "PATCH")

        # Get Status of Finalizing Project
        self.assertEqual(
            responses.calls[5].request.url, "https://host_name.com/status/some-status/"
        )
        self.assertEqual(responses.calls[5].request.method, "GET")

        # Get Finalized Project
        self.assertEqual(responses.calls[6].request.url, "https://host_name.com/projects/p-id/")
        self.assertEqual(responses.calls[6].request.method, "GET")

    @responses.activate
    def test_set_target_featurelist(self):
        """
        proj.set_target('test_target', featurelist_id=...)
        """
        prep_successful_aim_responses()
        Project("p-id").set_target("a_target", featurelist_id="f-id-3")
        request_body = request_body_to_json(responses.calls[0].request)
        assert request_body["featurelistId"] == "f-id-3"

    @responses.activate
    def test_set_target_monotonicity(self):
        prep_successful_aim_responses()

        opts = AdvancedOptions(
            monotonic_increasing_featurelist_id="fi-id",
            monotonic_decreasing_featurelist_id="fd-id",
            only_include_monotonic_blueprints=True,
        )
        p = Project("p-id").set_target(
            "Forks", positive_class="None or Unspecified", advanced_options=opts
        )
        request_body = request_body_to_json(responses.calls[0].request)
        assert request_body == {
            "target": "Forks",
            "mode": "auto",
            "smartDownsampled": False,
            "monotonicIncreasingFeaturelistId": "fi-id",
            "monotonicDecreasingFeaturelistId": "fd-id",
            "onlyIncludeMonotonicBlueprints": True,
            "positiveClass": "None or Unspecified",
            "quickrun": True,
            "autopilotWithFeatureDiscovery": False,
            "featureDiscoverySupervisedFeatureReduction": True,
        }
        self.assertEqual(responses.calls[0].request.method, "PATCH")
        self.assertEqual(responses.calls[1].request.method, "GET")
        self.assertIsInstance(p, Project)

    @responses.activate
    def test_attach_file_with_link_goes_to_url(self):
        """
        Project.create('https://google.com/file.csv')
        """
        prep_successful_project_creation_responses()

        link = "http:/google.com/datarobot.csv"
        Project.create(link)
        request_body = request_body_to_json(responses.calls[0].request)
        assert request_body == {
            "url": link,
            "projectName": "Untitled Project",
        }
        self.assertEqual(responses.calls[0].request.url, "https://host_name.com/projects/")

    @responses.activate
    def test_attach_file_with_file_path(self):
        """
        Project.create('synthetic-100.csv')
        """
        prep_successful_project_creation_responses()

        path = fixture_file_path("synthetic-100.csv")
        Project.create(path)

        self.assertEqual(responses.calls[0].request.url, "https://host_name.com/projects/")
        request_message = responses.calls[0].request.body
        with open(path, "rb") as fd:
            self.assertIn(fd.read(), request_message.read())

    @responses.activate
    def test_attach_file_with_non_csv_file_path(self):
        """
        Project.create('dataset.xlsx')
        """
        prep_successful_project_creation_responses()

        path = fixture_file_path("onehundredrows.xlsx")
        Project.create(path)
        self.assertEqual(responses.calls[0].request.url, "https://host_name.com/projects/")
        request_message = responses.calls[0].request.body.read()
        with open(path, "rb") as fd:
            self.assertIn(fd.read(), request_message)
        fname = re.search(b'filename="(.*)"', request_message).group(1)
        self.assertEqual(fname, b"onehundredrows.xlsx")

    @responses.activate
    def test_get_status_underscorizes(self):
        body = json.dumps(
            {"autopilotDone": True, "stage": "modeling", "stageDescription": "Ready for modeling"}
        )
        responses.add(
            responses.GET,
            "https://host_name.com/projects/p-id/status/",
            status=200,
            body=body,
            content_type="application/json",
        )
        status = Project("p-id").get_status()
        self.assertEqual(status["stage"], "modeling")
        self.assertTrue(status["autopilot_done"])

    @responses.activate
    def test_get_blueprints(self):
        responses.add(
            responses.GET,
            "https://host_name.com/projects/p-id/blueprints/",
            status=200,
            body=json.dumps(self.blueprint_api_resp),
            content_type="application/json",
        )
        menu = Project("p-id").get_blueprints()
        for item in menu:
            self.assertIsInstance(item, Blueprint)
            self.assertEqual(item.project_id, "p-id")
        bluepr1 = menu[0]
        bluepr2 = menu[1]
        self.assertIsInstance(bluepr1.processes, list)
        self.assertEqual(bluepr1.processes[0], "Regularized Linear Model Preprocessing v5")
        self.assertEqual(bluepr1.processes[1], "Log Transformed Response")
        self.assertEqual(
            bluepr1.model_type, "Auto-tuned K-Nearest Neighbors Regressor (Minkowski Distance)"
        )
        self.assertIsInstance(bluepr2.processes, list)
        self.assertEqual(bluepr2.processes[0], "Regularized Linear Model Preprocessing v12")
        self.assertEqual(bluepr2.processes[1], "Log Transformed Response")
        self.assertEqual(bluepr2.model_type, "Auto-tuned Stochastic Gradient Descent Regression")

    @responses.activate
    def test_get_monotonicity_blueprints(self):
        mono_config = {
            "supportsMonotonicConstraints": True,
            "monotonicDecreasingFeaturelistId": "5ae04c0d962d7410683073cb",
            "monotonicIncreasingFeaturelistId": "5ae04c0f962d7410683073cc",
        }
        blueprint_resp = [dict(**b) for b in self.blueprint_api_resp]
        [b.update(mono_config) for b in blueprint_resp]
        responses.add(
            responses.GET,
            "https://host_name.com/projects/p-id/blueprints/",
            status=200,
            body=json.dumps(blueprint_resp),
            content_type="application/json",
        )
        blueprints = Project("p-id").get_blueprints()
        for blueprint in blueprints:
            assert (
                blueprint.monotonic_increasing_featurelist_id
                == mono_config["monotonicIncreasingFeaturelistId"]
            )
            assert (
                blueprint.monotonic_decreasing_featurelist_id
                == mono_config["monotonicDecreasingFeaturelistId"]
            )
            assert (
                blueprint.supports_monotonic_constraints
                == mono_config["supportsMonotonicConstraints"]
            )

    @responses.activate
    def test_class_mapping_aggregation_settings_ignored_on_nonmulticlass(self):
        """These settings only make sense for multiclass, check the object is ignored
        if target type isn't multiclass"""
        prep_successful_aim_responses()
        cmas = ClassMappingAggregationSettings(min_class_support=5)
        Project("p-id").set_target("target", class_mapping_aggregation_settings=cmas)
        request_body = request_body_to_json(responses.calls[0].request)
        assert "classMappingAggregationSettings" not in request_body

    @responses.activate
    def test_class_mapping_aggregation_settings_partially_filled_multiclass(self):
        """Test partially filled ClassMappingAggregationSettings pass only filled fields"""
        prep_successful_aim_responses()
        cmas = ClassMappingAggregationSettings(min_class_support=5)
        Project("p-id").set_target(
            "target", target_type=TARGET_TYPE.MULTICLASS, class_mapping_aggregation_settings=cmas
        )
        request_body = request_body_to_json(responses.calls[0].request)
        assert request_body["classMappingAggregationSettings"] == {"minClassSupport": 5}

    @responses.activate
    def test_class_mapping_aggregation_settings_partially_filled_multilabel(self):
        """Test partially filled ClassMappingAggregationSettings pass only filled fields"""
        prep_successful_aim_responses()
        cmas = ClassMappingAggregationSettings(min_class_support=5)
        Project("p-id").set_target(
            "target", target_type=TARGET_TYPE.MULTILABEL, class_mapping_aggregation_settings=cmas
        )
        request_body = request_body_to_json(responses.calls[0].request)
        assert request_body["classMappingAggregationSettings"] == {"minClassSupport": 5}

    @responses.activate
    def test_class_mapping_aggregation_settings_full(self):
        """Test ClassMappingAggregationSettings can pass all 4 fields"""
        prep_successful_aim_responses()
        cmas = ClassMappingAggregationSettings(
            max_unaggregated_class_values=10,
            min_class_support=5,
            excluded_from_aggregation=["class1", "class2"],
            aggregation_class_name="Catch All",
        )
        Project("p-id").set_target(
            "target", target_type=TARGET_TYPE.MULTICLASS, class_mapping_aggregation_settings=cmas
        )
        request_body = request_body_to_json(responses.calls[0].request)
        assert request_body["classMappingAggregationSettings"] == {
            "aggregationClassName": "Catch All",
            "excludedFromAggregation": ["class1", "class2"],
            "maxUnaggregatedClassValues": 10,
            "minClassSupport": 5,
        }

    @responses.activate
    def test_set_exponentially_weighted_moving_alpha(self):
        """
        Test setting exponentially weighted moving alpha
        """
        prep_successful_aim_responses()

        opts = AdvancedOptions(exponentially_weighted_moving_alpha=0.9)
        Project("p-id").set_target("SalePrice", advanced_options=opts)

        request_body = request_body_to_json(responses.calls[0].request)
        assert request_body["exponentiallyWeightedMovingAlpha"] == 0.9

    @responses.activate
    def test_set_external_time_series_baseline_dataset_id(self):
        """
        Test setting external time series baseline dataset in advanced options
        """
        prep_successful_aim_responses()

        opts = AdvancedOptions(external_time_series_baseline_dataset_id="beefbeef")
        Project("p-id").set_target("SalePrice", advanced_options=opts)

        request_body = request_body_to_json(responses.calls[0].request)
        assert request_body["externalTimeSeriesBaselineDatasetId"] == "beefbeef"


@responses.activate
def test_create_featurelist(featurelist_server_data, project_id):
    project = Project(project_id)
    name = featurelist_server_data["name"]
    features = featurelist_server_data["features"]

    responses.add(
        responses.POST,
        "https://host_name.com/projects/{}/featurelists/".format(project_id),
        json=featurelist_server_data,
        status=201,
        content_type="application/json",
        adding_headers={
            "Location": "https://host_name.com/projects/{}/featurelists/{}/".format(
                project_id, featurelist_server_data["id"]
            )
        },
    )
    new_flist = project.create_featurelist(name, features)
    assert new_flist.name == name
    assert new_flist.features == features
    assert new_flist.project_id == project_id
    assert new_flist.num_models == featurelist_server_data["numModels"]
    assert new_flist.is_user_created == featurelist_server_data["isUserCreated"]
    assert new_flist.description == featurelist_server_data["description"]
    assert isinstance(new_flist.created, datetime.datetime)


class TestProjectJobListing(SDKTestcase):
    job1_queued_dict = {
        "status": "queue",
        "processes": ["Majority Class Classifier"],
        "projectId": "556902e8100d2b3728d47551",
        "samplePct": 32.0,
        "modelType": "Majority Class Classifier",
        "featurelistId": "556902eb100d2b37d1130771",
        "blueprintId": "89e08076a908e859c07af49bd4aa6a0f",
        "id": "10",
        "isBlocked": False,
        "modelId": "556902ef100d2b37da13077c",
    }
    job2_queued_dict = {
        "status": "queue",
        "processes": ["One-Hot Encoding", "Missing Values Imputed", "RuleFit Classifier"],
        "projectId": "556902e8100d2b3728d47551",
        "samplePct": 32.0,
        "modelType": "RuleFit Classifier",
        "featurelistId": "556902eb100d2b37d1130771",
        "blueprintId": "a8959bc1d46f07fb3dc14db7c1e3fc99",
        "id": "11",
        "isBlocked": False,
        "modelId": "556902ef100d2b37da13077d",
    }
    job3_queued_dict = {
        "status": "queue",
        "processes": ["One-Hot Encoding", "Missing Values Imputed", "RuleFit Classifier"],
        "projectId": "556902e8100d2b3728d47551",
        "samplePct": 64.0,
        "modelType": "RuleFit Classifier",
        "featurelistId": "556902eb100d2b37d1130771",
        "blueprintId": "a8959bc1d46f07fb3dc14db7c1e3fc99",
        "id": "17",
        "isBlocked": False,
        "modelId": "556902ef100d2b37da13077d",
    }
    job1_inprogress_dict = dict(job1_queued_dict, status="inprogress")
    job2_inprogress_dict = dict(job2_queued_dict, status="inprogress")

    predict_job_queued_dict = {
        "status": "queue",
        "projectId": "56b62892ccf94e7e939c89c8",
        "message": "",
        "id": "27",
        "isBlocked": False,
        "modelId": "56b628b7ccf94e0444bb8152",
    }

    predict_job_errored_dict = {
        "status": "error",
        "projectId": "56b62892ccf94e7e939c89c8",
        "message": "",
        "id": "23",
        "isBlocked": False,
        "modelId": "56b628b7ccf94e0444bb8152",
    }

    all_jobs_response = {
        "count": 4,
        "next": None,
        "jobs": [
            {
                "status": "inprogress",
                "url": "https://host_name.com/projects/p-id/modelJobs/1/",
                "id": "1",
                "jobType": "model",
                "isBlocked": False,
                "projectId": "p-id",
            },
            {
                "status": "inprogress",
                "url": "https://host_name.com/projects/p-id/modelJobs/2/",
                "id": "2",
                "jobType": "model",
                "isBlocked": False,
                "projectId": "p-id",
            },
            {
                "status": "queue",
                "url": "https://host_name.com/projects/p-id/predictJobs/3/",
                "id": "3",
                "jobType": "predict",
                "isBlocked": False,
                "projectId": "p-id",
            },
            {
                "status": "queue",
                "url": "https://host_name.com/projects/p-id/modelJobs/4/",
                "id": "4",
                "jobType": "model",
                "isBlocked": False,
                "projectId": "p-id",
            },
        ],
        "previous": None,
    }

    all_error_jobs_response = {
        "count": 1,
        "next": None,
        "jobs": [
            {
                "status": "error",
                "url": "https://host_name.com/projects/p-id/predictJobs/3/",
                "id": "3",
                "jobType": "predict",
                "isBlocked": False,
                "projectId": "p-id",
            }
        ],
        "previous": None,
    }

    @responses.activate
    def test_get_all_jobs(self):
        body = json.dumps(self.all_jobs_response)
        responses.add(
            responses.GET,
            "https://host_name.com/projects/p-id/jobs/",
            status=200,
            body=body,
            content_type="application/json",
        )
        jobs = Project("p-id").get_all_jobs()
        self.assertEqual(len(jobs), 4)

    @responses.activate
    def test_get_all_errored_jobs(self):
        body = json.dumps(self.all_error_jobs_response)
        responses.add(
            responses.GET,
            "https://host_name.com/projects/p-id/jobs/",
            status=200,
            body=body,
            content_type="application/json",
        )
        jobs = Project("p-id").get_all_jobs(status=QUEUE_STATUS.ERROR)
        self.assertEqual(
            responses.calls[0].request.url, "https://host_name.com/projects/p-id/jobs/?status=error"
        )
        self.assertEqual(len(jobs), 1)

    @responses.activate
    def test_get_model_jobs(self):
        job_dict = self.job1_queued_dict
        body = json.dumps([job_dict])
        responses.add(
            responses.GET,
            "https://host_name.com/projects/p-id/modelJobs/",
            status=200,
            body=body,
            content_type="application/json",
        )
        jobs = Project("p-id").get_model_jobs(status=QUEUE_STATUS.QUEUE)
        self.assertEqual(
            responses.calls[0].request.url,
            "https://host_name.com/projects/p-id/modelJobs/?status=queue",
        )
        self.assertEqual(len(jobs), 1)
        received_dict = jobs[0].__dict__
        expected_dict = ModelJob(job_dict).__dict__
        # because two `Model()` instances don't count as equal even if
        # their IDs are equal, we have to compare them separately.
        received_model = received_dict.pop("model")
        expected_model = expected_dict.pop("model")
        assert received_model.id == expected_model.id
        assert received_dict == expected_dict

    @responses.activate
    def test_get_model_jobs_requests_all_by_default(self):
        job_dict = self.job1_queued_dict
        body = json.dumps([job_dict])
        responses.add(
            responses.GET,
            "https://host_name.com/projects/p-id/modelJobs/",
            status=200,
            body=body,
            content_type="application/json",
        )
        jobs = Project("p-id").get_model_jobs()
        self.assertEqual(
            responses.calls[0].request.url, "https://host_name.com/projects/p-id/modelJobs/"
        )
        self.assertEqual(len(jobs), 1)
        received_dict = jobs[0].__dict__
        expected_dict = ModelJob(job_dict).__dict__
        # because two `Model()` instances don't count as equal even if
        # their IDs are equal, we have to compare them separately.
        received_model = received_dict.pop("model")
        expected_model = expected_dict.pop("model")
        assert received_model.id == expected_model.id
        assert received_dict == expected_dict

    @responses.activate
    def test_get_predict_jobs(self):
        body = json.dumps([self.predict_job_errored_dict])
        responses.add(
            responses.GET,
            "https://host_name.com/projects/p-id/predictJobs/",
            status=200,
            body=body,
            content_type="application/json",
        )
        jobs = Project("p-id").get_predict_jobs(status=QUEUE_STATUS.ERROR)
        self.assertEqual(
            responses.calls[0].request.url,
            "https://host_name.com/projects/p-id/predictJobs/?status=error",
        )
        self.assertEqual(len(jobs), 1)
        result_job = jobs[0]
        expected_job = PredictJob(self.predict_job_errored_dict)
        self.assertEqual(expected_job.id, result_job.id)
        self.assertEqual(expected_job.project, result_job.project)

    @responses.activate
    def test_get_predict_jobs_default(self):
        body = json.dumps([self.predict_job_queued_dict])
        responses.add(
            responses.GET,
            "https://host_name.com/projects/p-id/predictJobs/",
            status=200,
            body=body,
            content_type="application/json",
        )
        jobs = Project("p-id").get_predict_jobs()
        self.assertEqual(
            responses.calls[0].request.url, "https://host_name.com/projects/p-id/predictJobs/"
        )
        self.assertEqual(len(jobs), 1)
        result_job = jobs[0]
        expected_job = PredictJob(self.predict_job_queued_dict)
        self.assertEqual(expected_job.id, result_job.id)
        self.assertEqual(expected_job.project, result_job.project)

    @patch("datarobot.Project.get_model_jobs")
    def test_job_status_counter(self, mock_get_jobs):
        project = Project("p-id")
        jobs0 = []
        jobs1 = [ModelJob(self.job1_queued_dict)]
        jobs2 = [ModelJob(self.job1_inprogress_dict), ModelJob(self.job2_queued_dict)]
        jobs3 = [ModelJob(self.job2_inprogress_dict)]
        mock_get_jobs.side_effect = [jobs0, jobs1, jobs2, jobs3]
        assert project._get_job_status_counts() == (0, 0)
        assert project._get_job_status_counts() == (0, 1)
        assert project._get_job_status_counts() == (1, 1)
        assert project._get_job_status_counts() == (1, 0)

    def test_wait_for_autopilot(self):
        def make_status(autopilot_done):
            return {"autopilot_done": autopilot_done}

        project = Project("p-id")
        with mock.patch.object(Project, "_autopilot_status_check") as mock_autopilot_check:
            mock_autopilot_check.side_effect = (
                [make_status(False)] * 3 + [make_status(True)] + [make_status(False)]
            )

            project.wait_for_autopilot(check_interval=0.5, verbosity=0)
            assert mock_autopilot_check.call_count == 4

    def test_wait_for_autopilot_timeout(self):
        project = Project("p-id")
        with mock.patch.object(Project, "_autopilot_status_check") as mock_autopilot_check:
            mock_autopilot_check.return_value = {"autopilot_done": False}
            self.assertRaises(
                errors.AsyncTimeoutError,
                project.wait_for_autopilot,
                check_interval=10,
                verbosity=0,
                timeout=0.2,
            )

    def test_wait_for_autopilot_target_not_set_is_error(self):
        project = Project("p-id")
        with mock.patch.object(Project, "get_status") as mock_get_status:
            mock_get_status.return_value = {
                "autopilot_done": False,
                "stage": PROJECT_STAGE.AIM,
            }
            with pytest.raises(RuntimeError) as exc_info:
                project.wait_for_autopilot(check_interval=10, verbosity=0, timeout=0.2)
            assert_raised_regex(exc_info, "target has not been set")

    def test_wait_for_autopilot_mode_incorrect_is_error(self):
        project = Project("p-id")
        with mock.patch.multiple(
            Project,
            get_status=lambda _self: {"autopilot_done": False, "stage": PROJECT_STAGE.MODELING},
            _server_data=lambda _self, _: construct_dummy_aimed_project(autopilot_mode=2),
        ):
            with pytest.raises(RuntimeError) as exc_info:
                project.wait_for_autopilot(check_interval=10, verbosity=0, timeout=0.2)

            assert_raised_regex(exc_info, "mode is not full auto")


class TestProjectList(SDKTestcase):
    def setUp(self):
        self.raw_return = """
        [
            {
            "project_name": "Api project",
            "_id": "54c627fa100d2b2c7002a489"
            },
            {
            "_id": "54c78125100d2b2fe3b296b6",
            "project_name": "Untitled project"
            }
        ]
        """

    @responses.activate
    def test_list_projects(self):
        """
        Test list projects
        """
        responses.add(
            responses.GET,
            "https://host_name.com/projects/",
            body=self.raw_return,
            status=200,
            content_type="application/json",
        )
        project_lists = Project.list()
        assert isinstance(project_lists, list)
        assert project_lists[0].id == "54c627fa100d2b2c7002a489"
        assert project_lists[0].project_name == "Api project"
        assert project_lists[1].id == "54c78125100d2b2fe3b296b6"
        assert project_lists[1].project_name == "Untitled project"

    @responses.activate
    def test_with_manual_search_params(self):
        responses.add(
            responses.GET,
            "https://host_name.com/projects/?projectName=x",
            body=self.raw_return,
            status=200,
            content_type="application/json",
            match_querystring=True,
        )
        Project("p-id").list(search_params={"project_name": "x"})
        self.assertEqual(
            responses.calls[0].request.url, "https://host_name.com/projects/?projectName=x"
        )

    @responses.activate
    def test_with_bad_search_params(self):
        with self.assertRaises(TypeError):
            Project("p-id").list(search_params=12)


class TestGetModels(SDKTestcase, URLParamsTestCase):
    def setUp(self):
        super(TestGetModels, self).setUp()
        self.raw_data = """
        [
    {
    "featurelistId": "556cdfbd100d2b10048c7941",
    "processes": ["One", "Two", "Three"],
    "featurelistName": "Informative Features",
    "projectId": "p-id",
    "samplePct": 64,
    "modelType": "AVG Blender",
    "metrics": {
        "AUC": {
            "holdout": 0.76603,
            "validation": 0.64141,
            "crossValidation": 0.7625240000000001
        },
        "Rate@Top5%": {
            "holdout": 1,
            "validation": 0.5,
            "crossValidation": 0.9
        },
        "Rate@TopTenth%": {
            "holdout": 1,
            "validation": 1,
            "crossValidation": 1
        },
        "RMSE": {
            "holdout": 0.42054,
            "validation": 0.44396,
            "crossValidation": 0.40162000000000003
        },
        "LogLoss": {
            "holdout": 0.53707,
            "validation": 0.58051,
            "crossValidation": 0.5054160000000001
        },
        "FVE Binomial": {
            "holdout": 0.17154,
            "validation": 0.03641,
            "crossValidation": 0.17637399999999998
        },
        "Gini Norm": {
            "holdout": 0.53206,
            "validation": 0.28282,
            "crossValidation": 0.525048
        },
        "Rate@Top10%": {
            "holdout": 1,
            "validation": 0.25,
            "crossValidation": 0.7
        }
    },
    "blueprintId": "a4fd9d17a8ca62ee00590dd704dae6a8",
    "id": "556ce973100d2b6e51ca9657"
},
    {
    "featurelistId": "556cdfbd100d2b10048c7941",
    "processes": ["One", "Two", "Three"],
    "featurelistName": "Informative Features",
    "projectId": "p-id",
    "samplePct": 64,
    "modelType": "AVG Blender",
    "metrics": {
        "AUC": {
            "holdout": 0.76603,
            "validation": 0.64141,
            "crossValidation": 0.7625240000000001
        },
        "Rate@Top5%": {
            "holdout": 1,
            "validation": 0.5,
            "crossValidation": 0.9
        },
        "Rate@TopTenth%": {
            "holdout": 1,
            "validation": 1,
            "crossValidation": 1
        },
        "RMSE": {
            "holdout": 0.42054,
            "validation": 0.44396,
            "crossValidation": 0.40162000000000003
        },
        "LogLoss": {
            "holdout": 0.53707,
            "validation": 0.58051,
            "crossValidation": 0.5054160000000001
        },
        "FVE Binomial": {
            "holdout": 0.17154,
            "validation": 0.03641,
            "crossValidation": 0.17637399999999998
        },
        "Gini Norm": {
            "holdout": 0.53206,
            "validation": 0.28282,
            "crossValidation": 0.525048
        },
        "Rate@Top10%": {
            "holdout": 1,
            "validation": 0.25,
            "crossValidation": 0.7
        }
    },
    "blueprintId": "a4fd9d17a8ca62ee00590dd704dae6a8",
    "id": "556ce973100d2b6e51ca9658"
}
]
        """

    @responses.activate
    def test_get_models_ordered_by_metric_by_default(self):
        """
        Project('project-id').get_models()
        """
        responses.add(
            responses.GET,
            "https://host_name.com/projects/p-id/models/?orderBy=-metric",
            body=self.raw_data,
            status=200,
            content_type="application/json",
            match_querystring=True,
        )
        leaderboard = Project("p-id").get_models()
        self.assertNotEqual(0, len(leaderboard))
        for item in leaderboard:
            self.assertIsInstance(item, Model)
        self.assertEqual(leaderboard[0].id, "556ce973100d2b6e51ca9657")
        self.assertEqual(leaderboard[1].id, "556ce973100d2b6e51ca9658")
        self.assertEqual(leaderboard[0].project_id, "p-id")
        self.assertEqual(leaderboard[1].project_id, "p-id")

    @responses.activate
    def test_get_models_ordered_by_specific_field(self):
        # ordering
        responses.add(
            responses.GET,
            "https://host_name.com/projects/p-id/models/?orderBy=samplePct",
            body=self.raw_data,
            status=200,
            content_type="application/json",
            match_querystring=True,
        )
        Project("p-id").get_models(order_by="samplePct")
        self.assertEqual(
            responses.calls[0].request.url,
            "https://host_name.com/projects/p-id/models/?orderBy=samplePct",
        )

    @responses.activate
    def test_get_models_orderd_by_two_fields(self):
        # ordering by two fields
        responses.add(
            responses.GET,
            "https://host_name.com/projects/p-id/models/?orderBy=samplePct%2C-metric",
            body=self.raw_data,
            status=200,
            content_type="application/json",
            match_querystring=True,
        )
        Project("p-id").get_models(order_by=["sample_pct", "-metric"])
        self.assertEqual(
            responses.calls[0].request.url,
            "https://host_name.com/projects/p-id/models/?orderBy=samplePct%2C-metric",
        )

    @responses.activate
    def test_get_models_two_order_fields_and_filtering(self):
        # ordering by two fields plus filtering
        responses.add(
            responses.GET,
            "https://host_name.com/projects/p-id/models/"
            "?withMetric=RMSE&orderBy=metric%2C-samplePct",
            body=self.raw_data,
            status=200,
            content_type="application/json",
            match_querystring=True,
        )
        Project("p-id").get_models(order_by=["metric", "-sample_pct"], with_metric="RMSE")

    @responses.activate
    def test_get_monotonicity_models(self):
        mono_config = {
            "supportsMonotonicConstraints": True,
            "monotonicIncreasingFeaturelistId": "5ae04c0d962d7410683073cb",
            "monotonicDecreasingFeaturelistId": "5ae04c0f962d7410683073cc",
        }
        models_resp = json.loads(self.raw_data)
        [m.update(mono_config) for m in models_resp]
        responses.add(
            responses.GET,
            "https://host_name.com/projects/p-id/models/?withMetric=RMSE&orderBy=-metric",
            body=json.dumps(models_resp),
            status=200,
            content_type="application/json",
            match_querystring=True,
        )

        models = Project("p-id").get_models(with_metric="RMSE")

        for model in models:
            assert (
                model.supports_monotonic_constraints == mono_config["supportsMonotonicConstraints"]
            )
            assert (
                model.monotonic_increasing_featurelist_id
                == mono_config["monotonicIncreasingFeaturelistId"]
            )
            assert (
                model.monotonic_decreasing_featurelist_id
                == mono_config["monotonicDecreasingFeaturelistId"]
            )

    def test_order_by_with_unexpected_param_fails(self):
        with pytest.raises(ValueError) as exc_info:
            Project("p-id").get_models(order_by="someThing")
        assert_raised_regex(exc_info, "Provided order_by attribute")

    def test_order_by_with_bad_param_fails(self):
        with pytest.raises(TypeError) as exc_info:
            Project("p-id").get_models(order_by=True)
        assert_raised_regex(exc_info, "Provided order_by attribute")

    def test_with_bad_search_param_fails(self):
        with self.assertRaises(TypeError):
            Project("p-id").get_models(search_params=True)

    def _canonize_order_by_handles_none(self):
        proj = Project("p-id")
        self.assertIsNone(proj._canonize_order_by(None))

    @responses.activate
    def test_get_models_search_starred(self):
        responses.add(
            responses.GET,
            "https://host_name.com/projects/p-id/models/?orderBy=-metric&isStarred=false",
            body=self.raw_data,
            status=200,
            content_type="application/json",
            match_querystring=True,
        )
        Project("p-id").get_models(search_params={"is_starred": False})
        assert_urls_equal(
            responses.calls[0].request.url,
            "https://host_name.com/projects/p-id/models/?orderBy=-metric&isStarred=false",
        )


@responses.activate
def retrieve_smart_sampled_project(project_url, project_id, smart_sampled_project_server_data):
    responses.add(
        responses.GET,
        project_url,
        body=json.dumps(smart_sampled_project_server_data),
        status=200,
        content_type="application/json",
    )
    smart_sampled_project = Project.get(project_id)
    advanced = smart_sampled_project.advanced_options
    assert advanced["smart_downsampled"] is True
    rate_key = "majority_downsampling_rate"
    assert advanced[rate_key] == smart_sampled_project_server_data[rate_key]


@responses.activate
def test_get_rating_tables(
    rating_table_backend_generated_json,
    rating_table_uploaded_but_not_modeled_json,
    rating_table_uploaded_and_modeled_json,
):

    sample_rating_tables = json.dumps(
        {
            "data": [
                json.loads(rating_table_backend_generated_json),
                json.loads(rating_table_uploaded_but_not_modeled_json),
                json.loads(rating_table_uploaded_and_modeled_json),
            ]
        }
    )

    responses.add(
        responses.GET,
        "https://host_name.com/projects/p-id/ratingTables/",
        body=sample_rating_tables,
        status=200,
        content_type="application/json",
    )
    rating_tables = Project("p-id").get_rating_tables()

    assert len(rating_tables) == 3
    for rt in rating_tables:
        assert isinstance(rt, RatingTable)
        assert rt.id


@responses.activate
def test_get_rating_tables_no_tables():

    sample_rating_tables = json.dumps({"data": []})

    responses.add(
        responses.GET,
        "https://host_name.com/projects/p-id/ratingTables/",
        body=sample_rating_tables,
        status=200,
        content_type="application/json",
    )
    rating_tables = Project("p-id").get_rating_tables()

    assert len(rating_tables) == 0


@responses.activate
def test_get_rating_table_models(rating_table_model_server_data):
    sample_rating_table_model = json.dumps(
        [rating_table_model_server_data, rating_table_model_server_data]
    )

    responses.add(
        responses.GET,
        "https://host_name.com/projects/p-id/ratingTableModels/",
        body=sample_rating_table_model,
        status=200,
        content_type="application/json",
    )
    rating_table_models = Project("p-id").get_rating_table_models()

    assert len(rating_table_models) == 2
    for rtm in rating_table_models:
        assert isinstance(rtm, RatingTableModel)
        assert rtm.id
        assert rtm.rating_table_id


@responses.activate
def test_get_rating_table_models_no_models():
    responses.add(
        responses.GET,
        "https://host_name.com/projects/p-id/ratingTableModels/",
        body="[]",
        status=200,
        content_type="application/json",
    )
    rating_table_models = Project("p-id").get_rating_table_models()

    assert len(rating_table_models) == 0


@responses.activate
@pytest.mark.parametrize("extra_keys", [{}, {"newKey": "blah"}])
def test_get_access_list(project_server_data, project_endpoint, extra_keys):
    project = Project.from_server_data(project_server_data)
    access_list = {
        "data": [
            {
                "username": "me@datarobot.com",
                "userId": "1234deadbeeffeeddead4321",
                "role": "OWNER",
                "canShare": True,
            }
        ],
        "count": 1,
        "previous": None,
        "next": None,
    }
    access_record = access_list["data"][0]
    access_record.update(extra_keys)
    responses.add(
        responses.GET, "{}{}/accessControl/".format(project_endpoint, project.id), json=access_list
    )

    response = project.get_access_list()
    assert len(response) == 1

    share_info = response[0]
    assert share_info.username == access_record["username"]
    assert share_info.user_id == access_record["userId"]
    assert share_info.role == access_record["role"]
    assert share_info.can_share == access_record["canShare"]


@responses.activate
def test_share(project_endpoint, project_server_data):
    project = Project.from_server_data(project_server_data)
    request = SharingAccess("me@datarobot.com", "EDITOR")
    responses.add(
        responses.PATCH, "{}{}/accessControl/".format(project_endpoint, project.id), status=204
    )

    project.share([request])

    actual_payload = request_body_to_json(responses.calls[0].request)
    assert actual_payload == {"data": [{"username": "me@datarobot.com", "role": "EDITOR"}]}


@responses.activate
def test_remove_share(project_endpoint, project_server_data):
    project = Project.from_server_data(project_server_data)
    request = SharingAccess("me@datarobot.com", None)
    responses.add(
        responses.PATCH, "{}{}/accessControl/".format(project_endpoint, project.id), status=204
    )

    project.share([request])

    actual_payload = request_body_to_json(responses.calls[0].request)
    assert actual_payload == {"data": [{"username": "me@datarobot.com", "role": None}]}


@responses.activate
def test_share_with_grant(project_endpoint, project_server_data):
    project = Project.from_server_data(project_server_data)
    responses.add(
        responses.PATCH, "{}{}/accessControl/".format(project_endpoint, project.id), status=204
    )

    project.share(
        [
            SharingAccess("me@datarobot.com", "EDITOR", can_share=True),
            SharingAccess("other@datarobot.com", "CONSUMER", can_share=False),
        ]
    )

    actual_payload = request_body_to_json(responses.calls[0].request)
    assert actual_payload == {
        "data": [
            {"username": "me@datarobot.com", "role": "EDITOR", "canShare": True},
            {"username": "other@datarobot.com", "role": "CONSUMER", "canShare": False},
        ]
    }


@responses.activate
@pytest.mark.parametrize("send_notification", [True, False])
def test_share_send_notification(send_notification, project_endpoint, project_server_data):
    project = Project.from_server_data(project_server_data)
    request = SharingAccess("me@datarobot.com", "EDITOR")
    responses.add(
        responses.PATCH, "{}{}/accessControl/".format(project_endpoint, project.id), status=204
    )

    project.share([request], send_notification=send_notification)

    actual_payload = request_body_to_json(responses.calls[0].request)
    assert actual_payload == {
        "data": [{"username": "me@datarobot.com", "role": "EDITOR"}],
        "sendNotification": send_notification,
    }


@responses.activate
@pytest.mark.parametrize("include_feature_discovery_entities", [True, False])
def test_share_include_feature_discovery_entities(
    include_feature_discovery_entities, project_endpoint, project_server_data
):
    project = Project.from_server_data(project_server_data)
    request = SharingAccess("me@datarobot.com", "EDITOR")
    responses.add(
        responses.PATCH, "{}{}/accessControl/".format(project_endpoint, project.id), status=204
    )

    project.share([request], include_feature_discovery_entities=include_feature_discovery_entities)

    actual_payload = request_body_to_json(responses.calls[0].request)
    assert actual_payload == {
        "data": [{"username": "me@datarobot.com", "role": "EDITOR"}],
        "includeFeatureDiscoveryEntities": include_feature_discovery_entities,
    }


@responses.activate
def test_create_interaction_feature(project_endpoint, project, interaction_feature_server_data):
    responses.add(
        responses.POST,
        "{}{}/interactionFeatures/".format(project_endpoint, project.id),
        body="",
        status=202,
        content_type="application/json",
        adding_headers={"Location": "https://host_name.com/status/status-id/"},
    )

    responses.add(
        responses.GET,
        "https://host_name.com/status/status-id/",
        status=303,
        body="",
        content_type="application/json",
        adding_headers={"Location": "https://host_name.com/projects/{}/".format(project.id)},
    )

    responses.add(
        responses.GET,
        "https://host_name.com/projects/{}/".format(project.id),
        status=200,
        body=json.dumps(interaction_feature_server_data),
        content_type="application/json",
    )

    project.create_interaction_feature("int0", ["cat1", "cat2"], "+")

    assert responses.calls[0].response.status_code == 202
    assert responses.calls[1].response.status_code == 303
    assert responses.calls[2].response.status_code == 200

    assert request_body_to_json(responses.calls[0].request) == {
        "featureName": "int0",
        "features": ["cat1", "cat2"],
        "separator": "+",
    }


def test_create_interaction_feature_arguments_validation(project):
    with pytest.raises(TypeError):
        project.create_interaction_feature("name", "f1 & f2", "+")

    with pytest.raises(ValueError):
        project.create_interaction_feature("name", ["f1", "f2", "f2"], "+")


@responses.activate
def test_get_relationships_configuration(project, relationships_configuration):
    id = project.id
    responses.add(
        responses.GET,
        "https://host_name.com/projects/{}/relationshipsConfiguration/".format(id),
        json=relationships_configuration,
    )

    result = project.get_relationships_configuration()
    assert responses.calls[0].request.method == "GET"
    assert result.id == relationships_configuration["id"]
    assert len(result.dataset_definitions) == 2
    assert len(result.relationships) == 2

    for actual, expected in zip(
        result.dataset_definitions, relationships_configuration["datasetDefinitions"]
    ):
        assert actual["identifier"] == expected["identifier"]
        assert actual["catalog_version_id"] == expected["catalogVersionId"]
        assert actual["catalog_id"] == expected["catalogId"]
        assert actual["snapshot_policy"] == expected["snapshotPolicy"]

    actual = result.relationships[1]
    expected = relationships_configuration["relationships"][1]
    assert actual["dataset1_identifier"] == expected["dataset1Identifier"]
    assert actual["dataset2_identifier"] == expected["dataset2Identifier"]
    assert actual["dataset1_keys"] == expected["dataset1Keys"]
    assert actual["dataset2_keys"] == expected["dataset2Keys"]
    assert actual["feature_derivation_window_end"] == expected["featureDerivationWindowEnd"]
    assert actual["feature_derivation_window_start"] == expected["featureDerivationWindowStart"]
    assert (
        actual["feature_derivation_window_time_unit"] == expected["featureDerivationWindowTimeUnit"]
    )
    assert actual["prediction_point_rounding"] == expected["predictionPointRounding"]
    assert (
        actual["prediction_point_rounding_time_unit"] == expected["predictionPointRoundingTimeUnit"]
    )


@responses.activate
@pytest.mark.parametrize("mode", [AUTOPILOT_MODE.FULL_AUTO])
@pytest.mark.parametrize("blend_best_models", [True, False])
@pytest.mark.parametrize("scoring_code_only", [True, False])
@pytest.mark.parametrize("prepare_model_for_deployment", [True, False])
@pytest.mark.parametrize("consider_blenders_in_recommendation", [True, False])
@pytest.mark.parametrize("run_leakage_removed_feature_list", [True, False])
def test_start_autopilot(
    project_endpoint,
    project,
    mode,
    blend_best_models,
    scoring_code_only,
    prepare_model_for_deployment,
    consider_blenders_in_recommendation,
    run_leakage_removed_feature_list,
):
    responses.add(
        responses.POST,
        "{}{}/autopilots/".format(project_endpoint, project.id),
        status=201,
        content_type="application/json",
    )

    project.start_autopilot(
        "featurelist-id",
        mode=mode,
        blend_best_models=blend_best_models,
        scoring_code_only=scoring_code_only,
        prepare_model_for_deployment=prepare_model_for_deployment,
        consider_blenders_in_recommendation=consider_blenders_in_recommendation,
        run_leakage_removed_feature_list=run_leakage_removed_feature_list,
    )
    actual_payload = request_body_to_json(responses.calls[0].request)
    assert actual_payload == {
        "featurelistId": "featurelist-id",
        "mode": mode,
        "blendBestModels": blend_best_models,
        "scoringCodeOnly": scoring_code_only,
        "prepareModelForDeployment": prepare_model_for_deployment,
        "considerBlendersInRecommendation": consider_blenders_in_recommendation,
        "runLeakageRemovedFeatureList": run_leakage_removed_feature_list,
    }


@responses.activate
def test_start_prepare_model_for_deployment(project_endpoint, project):
    responses.add(
        responses.POST,
        "{}{}/deploymentReadyModels/".format(project_endpoint, project.id),
        status=201,
        content_type="application/json",
    )

    project.start_prepare_model_for_deployment("model-id")
    actual_payload = request_body_to_json(responses.calls[0].request)
    assert actual_payload == {"modelId": "model-id"}


@pytest.fixture
def dataset_content():
    return "some_random_file_contents" * 1000000


@pytest.fixture
def local_csv_filename(tmpdir):
    return str(tmpdir.join("temp.csv"))


@responses.activate
def test_feature_discovery_download_training_dataset(dataset_content, local_csv_filename):
    project_id = "pid"
    url = "https://host_name.com/projects/{}/featureDiscoveryDatasetDownload/".format(project_id)
    responses.add(responses.GET, url, body=dataset_content, status=200, match_querystring=True)
    project = Project(id=project_id)
    project.download_feature_discovery_dataset(local_csv_filename)
    assert os.path.isfile(local_csv_filename)
    with open(local_csv_filename) as f:
        contents = f.read()
        assert contents == dataset_content
    os.unlink(local_csv_filename)
    assert not os.path.isfile(local_csv_filename)


@responses.activate
def test_feature_discovery_download_prediction_dataset(dataset_content, local_csv_filename):
    project_id = "pid"
    dataset_id = "did"
    url = "https://host_name.com/projects/{}/featureDiscoveryDatasetDownload/?datasetId={}".format(
        project_id, dataset_id
    )
    responses.add(responses.GET, url, body=dataset_content, status=200, match_querystring=True)
    project = Project(id=project_id)
    project.download_feature_discovery_dataset(local_csv_filename, pred_dataset_id=dataset_id)
    assert os.path.isfile(local_csv_filename)
    with open(local_csv_filename) as f:
        contents = f.read()
        assert contents == dataset_content
    os.unlink(local_csv_filename)
    assert not os.path.isfile(local_csv_filename)


@pytest.fixture
def sql_content():
    return "some_random_sql_contents" * 1000000


@pytest.fixture
def local_sql_filename(tmpdir):
    return str(tmpdir.join("temp.sql"))


@responses.activate
def test_feature_discovery_download_project_sql(sql_content, local_sql_filename):
    pid = "pid"
    export_url = "https://host_name.com/projects/{}/featureDiscoveryRecipeSqlExports/".format(pid)
    download_url = "https://host_name.com/projects/{}/featureDiscoveryRecipeSQLs/download/"
    download_url = download_url.format(pid)

    responses.add(
        responses.POST,
        export_url,
        body="",
        status=202,
        adding_headers={"Location": "https://host_name.com/status/status-id/"},
    )
    responses.add(
        responses.GET,
        "https://host_name.com/status/status-id/",
        status=303,
        body="",
        content_type="application/json",
        adding_headers={"Location": download_url},
    )
    responses.add(
        responses.GET, download_url, status=200, body=sql_content, content_type="application/json",
    )

    project = Project(id=pid)
    project.download_feature_discovery_recipe_sqls(local_sql_filename)
    assert os.path.isfile(local_sql_filename)
    with open(local_sql_filename) as f:
        contents = f.read()
        assert contents == sql_content
    os.unlink(local_sql_filename)
    assert not os.path.isfile(local_sql_filename)


@responses.activate
def test_feature_discovery_download_model_sql(sql_content, local_sql_filename):
    pid = "pid"
    model_id = "lid"
    export_url = "https://host_name.com/projects/{}/featureDiscoveryRecipeSqlExports/".format(pid)
    download_url = "https://host_name.com/projects/{}/featureDiscoveryRecipeSQLs/download/"
    download_url = download_url.format(pid)
    download_url = "{}?modelId={}".format(download_url, model_id)

    responses.add(
        responses.POST,
        export_url,
        body="",
        status=202,
        adding_headers={"Location": "https://host_name.com/status/status-id/"},
    )
    responses.add(
        responses.GET,
        "https://host_name.com/status/status-id/",
        status=303,
        body="",
        content_type="application/json",
        adding_headers={"Location": download_url},
    )
    responses.add(
        responses.GET,
        download_url,
        status=200,
        body=sql_content,
        content_type="application/json",
        match_querystring=True,
    )

    project = Project(id=pid)
    project.download_feature_discovery_recipe_sqls(local_sql_filename, model_id=model_id)

    actual_payload = request_body_to_json(responses.calls[0].request)
    assert actual_payload == {"modelId": "lid"}

    assert os.path.isfile(local_sql_filename)
    with open(local_sql_filename) as f:
        contents = f.read()
        assert contents == sql_content
    os.unlink(local_sql_filename)
    assert not os.path.isfile(local_sql_filename)


@responses.activate
@pytest.mark.parametrize(
    "expected_content",
    [
        # no errors
        "feature,rowIndex,rowData,error\n",
        # one error
        "feature,rowIndex,rowData,error\nmc_0,17,['A'],invalid JSON\n",
        # multiple structurally different errors
        "feature,rowIndex,rowData,error\n"
        "mc_0,17.0,['A'],invalid JSON\n"
        "mc_0,,,too many labels\n",
        # errors in multiple features
        "feature,rowIndex,rowData,error\n"
        "mc_0,17,['A'],invalid JSON\n"
        "mc_1,5,['A'],invalid JSON\n",
        # unicode error
        'feature,rowIndex,rowData,error\nmc_0,0,"[""番号"", """"]",empty label name',
    ],
)
def test_download_multicategorical_data_format_errors(expected_content, local_csv_filename):
    pid = "pid"
    url = "https://host_name.com/projects/{}/multicategoricalInvalidFormat/file/".format(pid)
    responses.add(responses.GET, url, status=200, body=expected_content, content_type="text/csv")
    project = Project(id=pid)
    project.download_multicategorical_data_format_errors(file_name=local_csv_filename)
    assert os.path.isfile(local_csv_filename)
    with open(local_csv_filename) as f:
        contents = f.read()
        assert contents == expected_content
    os.unlink(local_csv_filename)
    assert not os.path.isfile(local_csv_filename)


def test_project_with_no_unsupervised_has_no_clustering():
    pid = "582e4309100d2b13b939b223"
    mock_client_patch = mock.MagicMock(return_value=mock.Mock(headers={"Location": None}))
    project = Project(id=pid)
    project._client.patch = mock_client_patch
    project.from_async = mock.MagicMock()
    project.refresh = mock.MagicMock()

    project.set_target(unsupervised_type="something", autopilot_cluster_list=[1, 2])
    assert mock_client_patch.call_count == 1
    actual_calls = mock_client_patch.call_args
    assert actual_calls[0][0] == "projects/{}/aim/".format(pid)
    assert actual_calls[1]["data"] == {
        "target": None,
        "mode": "auto",
        "metric": None,
        "quickrun": True,
    }


def test_project_with_clustering_has_type():
    pid = "582e4309100d2b13b939b223"
    mock_client_patch = mock.MagicMock(return_value=mock.Mock(headers={"Location": None}))
    project = Project(id=pid)
    project._client.patch = mock_client_patch
    project.from_async = mock.MagicMock()
    project.refresh = mock.MagicMock()

    project.set_target(unsupervised_mode=True, unsupervised_type=UnsupervisedTypeEnum.CLUSTERING)
    assert mock_client_patch.call_count == 1
    actual_calls = mock_client_patch.call_args
    assert actual_calls[0][0] == "projects/{}/aim/".format(pid)
    assert actual_calls[1]["data"] == {
        "target": None,
        "mode": "auto",
        "metric": None,
        "quickrun": True,
        "unsupervised_mode": True,
        "unsupervised_type": UnsupervisedTypeEnum.CLUSTERING,
    }


@pytest.mark.parametrize("autopilot_cluster_list", [1, 1.5, "a", (1, 2)])
def test_project_with_clustering_raises_for_invalid_autopilot_cluster_list(autopilot_cluster_list):
    project = Project("pid")
    with pytest.raises(ValueError):
        project.set_target(
            unsupervised_mode=True,
            unsupervised_type=UnsupervisedTypeEnum.CLUSTERING,
            autopilot_cluster_list=autopilot_cluster_list,
        )


def test_project_with_clustering_can_have_autopilot_cluster_list():
    pid = "582e4309100d2b13b939b223"
    mock_client_patch = mock.MagicMock(return_value=mock.Mock(headers={"Location": None}))
    project = Project(id=pid)
    project._client.patch = mock_client_patch
    project.from_async = mock.MagicMock()
    project.refresh = mock.MagicMock()

    project.set_target(
        unsupervised_mode=True,
        unsupervised_type=UnsupervisedTypeEnum.CLUSTERING,
        autopilot_cluster_list=[1, 2, 3],
    )
    assert mock_client_patch.call_count == 1
    actual_calls = mock_client_patch.call_args
    assert actual_calls[0][0] == "projects/{}/aim/".format(pid)
    assert actual_calls[1]["data"] == {
        "target": None,
        "mode": "auto",
        "metric": None,
        "quickrun": True,
        "unsupervised_mode": True,
        "unsupervised_type": UnsupervisedTypeEnum.CLUSTERING,
        "autopilot_cluster_list": [1, 2, 3],
    }
