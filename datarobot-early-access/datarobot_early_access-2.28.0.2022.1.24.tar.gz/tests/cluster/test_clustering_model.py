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
from datarobot.models.model import ClusteringModel
from datarobot.utils import from_api


class TestClusteringModel(object):
    def test_class_creation(self, clustering_model_data):
        model = ClusteringModel.from_data(from_api(clustering_model_data))
        # assert new fields specific to clustering models
        assert clustering_model_data["nClusters"] == model.n_clusters
        assert (
            clustering_model_data["isNClustersDynamicallyDetermined"]
            == model.is_n_clusters_dynamically_determined
        )
