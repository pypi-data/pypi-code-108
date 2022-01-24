# -*- coding: utf-8 -*-
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
from operator import itemgetter

import pytest
import responses
from trafaret import DataError

from datarobot import errors
from datarobot.models import FeatureAssociationMatrix
from datarobot.utils import from_api


@responses.activate
def test_get(project_id, feature_association_matrix_url, feature_association_matrix):
    responses.add(
        responses.GET,
        feature_association_matrix_url,
        status=200,
        content_type="application/json",
        body=json.dumps(feature_association_matrix),
    )
    feature_association = FeatureAssociationMatrix.get(project_id=project_id)
    assert feature_association
    assert feature_association.project_id == project_id
    assert len(feature_association.strengths) == len(feature_association_matrix["strengths"])
    assert len(feature_association.features) == len(feature_association_matrix["features"])
    assert sorted(feature_association.strengths, key=itemgetter("feature1")) == sorted(
        feature_association_matrix["strengths"], key=itemgetter("feature1")
    )
    assert sorted(feature_association.features, key=itemgetter("feature")) == sorted(
        from_api(feature_association_matrix["features"]), key=itemgetter("feature")
    )


@responses.activate
def test_get_for_featurelist(
    project_id, feature_association_matrix_url, feature_association_matrix
):
    featurelist_id = "6033e2b9ecb9108111e4c677"
    url = feature_association_matrix_url + "?featurelistId={}".format(featurelist_id)
    responses.add(
        responses.GET,
        url,
        status=200,
        content_type="application/json",
        body=json.dumps(feature_association_matrix),
    )
    feature_association = FeatureAssociationMatrix.get(
        project_id=project_id, featurelist_id=featurelist_id
    )
    assert feature_association
    assert feature_association.project_id == project_id
    assert len(feature_association.strengths) == len(feature_association_matrix["strengths"])
    assert len(feature_association.features) == len(feature_association_matrix["features"])
    assert sorted(feature_association.strengths, key=itemgetter("feature1")) == sorted(
        feature_association_matrix["strengths"], key=itemgetter("feature1")
    )
    assert sorted(feature_association.features, key=itemgetter("feature")) == sorted(
        from_api(feature_association_matrix["features"]), key=itemgetter("feature")
    )


@responses.activate
def test_get__not_found(project_id, feature_association_matrix_url):
    responses.add(responses.GET, feature_association_matrix_url, status=404)
    with pytest.raises(errors.ClientError, match="404 client error: "):
        FeatureAssociationMatrix.get(project_id=project_id)


@pytest.mark.parametrize("project_id", [None, "", 1, 42.1])
def test_get__invalid_project_id(project_id):
    with pytest.raises(DataError):
        FeatureAssociationMatrix.get(project_id)


def test_get__invalid_arguments(project_id):
    with pytest.raises(DataError):
        FeatureAssociationMatrix.get(
            project_id, metric="fake", association_type="fake", featurelist_id="",
        )
