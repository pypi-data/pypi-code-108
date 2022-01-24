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

from datarobot import errors, FeatureAssociationFeaturelists


@responses.activate
def test_get(
    project_id, feature_association_featurelists_url, feature_association_featurelists_data
):
    responses.add(
        responses.GET,
        feature_association_featurelists_url,
        status=200,
        content_type="application/json",
        body=json.dumps(feature_association_featurelists_data),
    )
    fam_featurelists = FeatureAssociationFeaturelists.get(project_id)

    assert len(fam_featurelists.featurelists) == 2
    for fam_featurelist in fam_featurelists.featurelists:
        assert set(fam_featurelist.keys()) == {"title", "has_fam", "featurelist_id"}


@responses.activate
def test_get__not_found(project_id, feature_association_featurelists_url):
    responses.add(responses.GET, feature_association_featurelists_url, status=404)
    with pytest.raises(errors.ClientError, match="404 client error: "):
        FeatureAssociationFeaturelists.get(project_id)
