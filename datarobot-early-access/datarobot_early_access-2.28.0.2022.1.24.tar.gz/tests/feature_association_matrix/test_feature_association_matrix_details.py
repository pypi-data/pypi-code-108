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

from datarobot import errors, FeatureAssociationMatrixDetails


@pytest.fixture
def feature1(feature_association_matrix_details_data):
    return feature_association_matrix_details_data["features"][0]


@pytest.fixture
def feature2(feature_association_matrix_details_data):
    return feature_association_matrix_details_data["features"][1]


@responses.activate
def test_get_feature_association_details(
    project_id,
    feature1,
    feature2,
    feature_association_matrix_details_url,
    feature_association_matrix_details_data,
):
    fam_url = feature_association_matrix_details_url.format(project_id, feature1, feature2)
    responses.add(
        responses.GET,
        fam_url,
        status=200,
        content_type="application/json",
        body=json.dumps(feature_association_matrix_details_data),
    )
    fam_details = FeatureAssociationMatrixDetails.get(
        project_id=project_id, feature1=feature1, feature2=feature2
    )

    assert set(fam_details.to_dict().keys()) == {"chart_type", "values", "features", "types"}
    assert len(fam_details.values) == len(feature_association_matrix_details_data["values"])
    assert fam_details.features == feature_association_matrix_details_data["features"]
    assert fam_details.types == feature_association_matrix_details_data["types"]
    assert fam_details.chart_type == feature_association_matrix_details_data["chart_type"]


@responses.activate
def test_get_feature_association_details__project_not_found(
    feature1, feature2, feature_association_matrix_details_url,
):
    non_existing_pid = "6034fcd7b9bc24be51493ad0"
    error = {"message": "Project with ID {} doesn't exist".format(non_existing_pid)}
    fam_url = feature_association_matrix_details_url.format(non_existing_pid, feature1, feature2)
    responses.add(
        responses.GET, fam_url, status=404, content_type="application/json", body=json.dumps(error),
    )
    with pytest.raises(
        errors.ClientError, match="Project with ID {} doesn't exist".format(non_existing_pid)
    ):
        FeatureAssociationMatrixDetails.get(
            project_id=non_existing_pid, feature1=feature1, feature2=feature2
        )


@responses.activate
def test_get_feature_association_details__feature_not_found(
    project_id, feature1, feature_association_matrix_details_url,
):
    non_existing_feature = "fake"
    error = {"message": "Invalid features were passed."}
    fam_url = feature_association_matrix_details_url.format(
        project_id, non_existing_feature, feature2
    )
    responses.add(
        responses.GET, fam_url, status=404, content_type="application/json", body=json.dumps(error),
    )
    with pytest.raises(errors.ClientError, match="Invalid features were passed."):
        FeatureAssociationMatrixDetails.get(
            project_id=project_id, feature1=non_existing_feature, feature2=feature2
        )
