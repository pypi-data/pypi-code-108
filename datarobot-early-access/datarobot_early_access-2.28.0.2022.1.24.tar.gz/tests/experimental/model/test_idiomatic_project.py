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
import json

import mock
import pytest
import responses

from datarobot._experimental import IdiomaticProject
from datarobot.enums import PROJECT_STAGE
from tests.utils import assert_raised_regex

# FIXTURES and HELPERS #############################################################################


@pytest.fixture
def feature_lists():
    return [
        {
            "id": "f-id-1",
            "projectId": "p-id",
            "name": "Raw Features",
            "features": ["One Fish", "Two Fish", "Red Fish", "Blue риба"],
        },
        {
            "id": "f-id-2",
            "projectId": "p-id",
            "name": "Informative Features",
            "features": ["One Fish", "Red Fish", "Blue риба"],
        },
        {
            "id": "f-id-3",
            "projectId": "p-id",
            "name": "Спеціальний список",
            "features": ["One Fish", "Blue риба"],
        },
    ]


@pytest.fixture
def new_feature_list():
    return {
        "id": "f-id-4",
        "projectId": "p-id",
        "name": "custom_list_1",
        "features": ["One Fish", "Blue риба"],
    }


@pytest.fixture
def idiomatic_project(project_with_target_data):
    return IdiomaticProject.from_data(project_with_target_data)


test_statuses = [
    {
        "autopilot_done": True,
        "stage": PROJECT_STAGE.MODELING,
        "stage_description": "Ready for modeling",
    },
    {"autopilot_done": False, "stage": PROJECT_STAGE.AIM, "stage_description": "Ready for aim"},
]


def test_time_series_not_supported(idiomatic_project):
    with mock.patch(
        "datarobot._experimental.IdiomaticProject.use_time_series",
        new_callable=mock.PropertyMock,
        return_value=True,
    ), pytest.raises(ValueError) as exc_info:
        idiomatic_project.fit()
        assert_raised_regex(exc_info, "Cannot currently run fit on timeseries projects")


@responses.activate
def test_fit_feature_lists(idiomatic_project, project_endpoint, feature_lists, new_feature_list):
    responses.add(
        responses.GET,
        "{}{}/featurelists/".format(project_endpoint, idiomatic_project.id),
        status=201,
        content_type="application/json",
        body=json.dumps(feature_lists),
    )

    responses.add(
        responses.POST,
        "{}{}/featurelists/".format(project_endpoint, idiomatic_project.id),
        status=201,
        content_type="application/json",
        body=json.dumps(new_feature_list),
    )

    with mock.patch.object(idiomatic_project, "start_autopilot"), mock.patch.object(
        idiomatic_project, "refresh"
    ), mock.patch.object(
        idiomatic_project, "get_status", return_value={"stage": PROJECT_STAGE.AIM}
    ), mock.patch.object(
        idiomatic_project, "set_target"
    ) as mock_set_target:
        # call by feature list id
        idiomatic_project.fit(feature_list="f-id-1")
        assert mock_set_target.called is True
        assert mock_set_target.call_args.kwargs["featurelist_id"] == "f-id-1"
        # call by feature list name -- default
        mock_set_target.reset_mock()
        idiomatic_project.fit(feature_list="Informative Features")
        assert mock_set_target.called is True
        assert mock_set_target.call_args.kwargs["featurelist_id"] == "f-id-2"
        # call by feature list name -- custom
        mock_set_target.reset_mock()
        idiomatic_project.fit(feature_list="Спеціальний список")
        assert mock_set_target.called is True
        assert mock_set_target.call_args.kwargs["featurelist_id"] == "f-id-3"
        # call by list of features
        mock_set_target.reset_mock()
        idiomatic_project.fit(feature_list=["One Fish", "Blue риба"])
        assert mock_set_target.called is True
        assert mock_set_target.call_args.kwargs["featurelist_id"] == "f-id-4"


@responses.activate
@pytest.mark.parametrize("status", test_statuses)
def test_fit(idiomatic_project, project_endpoint, feature_lists, status):
    responses.add(
        responses.GET,
        "{}{}/featurelists/".format(project_endpoint, idiomatic_project.id),
        status=201,
        content_type="application/json",
        body=json.dumps(feature_lists),
    )

    responses.add(
        responses.GET,
        "{}{}/status/".format(project_endpoint, idiomatic_project.id),
        status=201,
        content_type="application/json",
        body=json.dumps(status),
    )

    with mock.patch.object(idiomatic_project, "set_target") as mock_set_target, mock.patch.object(
        idiomatic_project, "start_autopilot"
    ) as mock_start_autopilot, mock.patch.object(idiomatic_project, "refresh"):
        idiomatic_project.fit()
        assert mock_set_target.called is not status["autopilot_done"]
        assert mock_start_autopilot.called is status["autopilot_done"]
