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

from datarobot import Project


@pytest.fixture
def project(project_with_target_data):
    return Project.from_data(project_with_target_data)


@responses.activate
def test_get_feature_association_details(
    project,
    project_id,
    feature_association_matrix_details_url,
    feature_association_matrix_details_data,
):
    feature1 = "area1"
    feature2 = "area2"
    responses.add(
        responses.GET,
        feature_association_matrix_details_url.format(project_id, feature1, feature2),
        status=200,
        content_type="application/json",
        body=json.dumps(feature_association_matrix_details_data),
    )
    feature_values = project.get_association_matrix_details(feature1="area1", feature2="area2")

    assert set(feature_values.keys()) == {"chart_type", "values", "features", "types"}
    assert len(feature_values["values"]) == 7
    assert feature_values["features"] == ["area1", "area2"]


@responses.activate
def test_get_feature_association_featurelists(
    feature_association_featurelists_data, feature_association_featurelists_url, project, project_id
):
    responses.add(
        responses.GET,
        feature_association_featurelists_url,
        status=200,
        content_type="application/json",
        body=json.dumps(feature_association_featurelists_data),
    )
    featurelists = project.get_association_featurelists()

    assert set(featurelists.keys()) == {"featurelists"}
    assert len(featurelists["featurelists"]) == 2
    assert featurelists["featurelists"][0]["title"] == "Informative Features"
    assert featurelists["featurelists"][0]["has_fam"] is True


@responses.activate
def test_get_feature_associations(
    project, feature_association_matrix_url, feature_association_matrix
):
    responses.add(
        responses.GET,
        feature_association_matrix_url,
        status=200,
        content_type="application/json",
        body=json.dumps(feature_association_matrix),
    )
    feature_associations = project.get_associations(metric=None, assoc_type=None)
    assert feature_associations
    assert set(feature_associations.keys()) == {"strengths", "features"}
