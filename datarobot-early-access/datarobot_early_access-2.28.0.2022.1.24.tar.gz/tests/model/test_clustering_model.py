# coding: utf-8
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

import responses

from datarobot.models.model import ClusteringModel


@responses.activate
def test_get_clustering_model_with_new_fields(
    project_url, project_id, model_id, clustering_models, project_clustering_data
):
    responses.add(responses.GET, project_url, body=json.dumps(project_clustering_data))

    for model_data in clustering_models:

        model_id = model_data["id"]

        responses.add(
            responses.GET,
            "{}models/{}/".format(project_url, model_id),
            body=json.dumps(model_data),
        )
        model = ClusteringModel.get(project_id, model_id)

        assert model.id == model_data["id"]
        assert model.model_type == model_data["modelType"]
        assert model.project_id == model_data["projectId"]
        # new fields
        assert model.n_clusters == model_data["nClusters"]
        assert (
            model.is_n_clusters_dynamically_determined
            == model_data["isNClustersDynamicallyDetermined"]
        )
        assert model.has_empty_clusters == model_data["hasEmptyClusters"]


def test_clustering_model_future_proof(clustering_model_gmm_server_data):
    data_with_future_keys = dict(clustering_model_gmm_server_data, new_key="new key")
    ClusteringModel.from_server_data(data_with_future_keys)
