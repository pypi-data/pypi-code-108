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

from datarobot.errors import ClientError
from datarobot.models import Cluster
from datarobot.utils import from_api


class TestCluster(object):
    def test_instantiation_no_percent(self, cluster_no_percent):
        """
        Given cluster data without optional value
        When I instantiate object
        Then objects fields hold expected data and optional filed is None
        """
        cl = Cluster.from_data(from_api(cluster_no_percent))
        assert cl.name == cluster_no_percent["name"]
        assert cl.percent is None

    def test_instantiation_with_percent(self, cluster_with_percent):
        """
        Given cluster data
        When I instantiate object
        Then objects fields hold expected data
        """
        cl = Cluster.from_data(from_api(cluster_with_percent))
        assert cl.name == cluster_with_percent["name"]
        assert cl.percent == cluster_with_percent["percent"]

    def test_future_proof(self, cluster_with_percent):
        """
        Given cluster data with new key
        When I instantiate object
        Then objects creates without errors and new key is ignored
        """
        new_key = "future"
        data = dict(from_api(cluster_with_percent), new_key=new_key)
        cl = Cluster.from_data(data)
        assert cl.__dict__.get(new_key) is None

    def test_repr(self, cluster_with_percent):
        """
        Given cluster instance
        When I print object using repr
        Then string value should match expected value
        """
        cl = Cluster.from_data(from_api(cluster_with_percent))
        assert str(cl) == "Cluster(name={}, percent={})".format(cl.name, cl.percent)

    # List cluster names
    @responses.activate
    def test_cluster_list_data(self, cluster_url, clusters_data, project_id, model_id):
        """
        Given valid response from api
        When I list cluster names
        Then order and values returned by method should match api response
        """
        responses.add(
            responses.GET,
            cluster_url,
            status=200,
            content_type="application/json",
            body=json.dumps(clusters_data),
        )
        cl = Cluster.list(project_id, model_id)
        assert len(cl) == len(clusters_data["clusters"])
        for idx, cluster in enumerate(cl):
            assert clusters_data["clusters"][idx]["name"] == cluster.name
            assert clusters_data["clusters"][idx]["percent"] == cluster.percent

    @responses.activate
    def test_cluster_list_not_found(self, cluster_url, clusters_data, project_id, model_id):
        """
        Given error response from with status_code 404
        When I list Clusters
        Then method should raise ClientError
        """
        responses.add(
            responses.GET,
            cluster_url,
            status=404,
            content_type="application/json",
            body=json.dumps({"message": "Not Found"}),
        )
        with pytest.raises(ClientError):
            Cluster.list(project_id, model_id)

    # Single cluster name update
    @responses.activate
    def test_update_name(self, cluster_url, clusters_data, project_id, model_id):
        """
        Given valid response from api
        When I update single name
        Then order and values returned by method should match api response
        """
        responses.add(
            responses.PATCH,
            cluster_url,
            status=200,
            content_type="application/json",
            body=json.dumps(clusters_data),
        )
        cl = Cluster.update_name(project_id, model_id, "Cluster 1", "New Name")
        assert len(cl) == len(clusters_data["clusters"])
        for idx, cluster in enumerate(cl):
            assert clusters_data["clusters"][idx]["name"] == cluster.name
            assert clusters_data["clusters"][idx]["percent"] == cluster.percent

    @responses.activate
    @pytest.mark.parametrize(
        "status_code,body",
        [
            (422, {"message": "No current cluster with name Cluster 1"}),
            (404, {"message": "Not Found"}),
        ],
    )
    def test_update_single_name_error(self, cluster_url, project_id, model_id, status_code, body):
        """
        Given error response from api with status_codes (404, 422)
        When I update single cluster name
        Then method should raise ClientError
        """
        responses.add(
            responses.PATCH,
            cluster_url,
            status=status_code,
            content_type="application/json",
            body=json.dumps(body),
        )
        with pytest.raises(ClientError):
            Cluster.update_name(project_id, model_id, "Cluster 1", "New Name")

    # Multiple cluster names update
    @responses.activate
    def test_update_multiple_names_ok(self, cluster_url, clusters_data, project_id, model_id):
        """
        Given valid response from api
        When I update multiple cluster names
        Then order and values returned by method should match api response
        """
        responses.add(
            responses.PATCH,
            cluster_url,
            status=200,
            content_type="application/json",
            body=json.dumps(clusters_data),
        )
        mappings = [
            ("old name 1", "new name 1"),
            ("old name 2", "new name 2"),
            ("old name 3", "new name 3"),
        ]
        cl = Cluster.update_multiple_names(project_id, model_id, mappings)
        assert len(cl) == len(clusters_data["clusters"])
        for idx, cluster in enumerate(cl):
            assert clusters_data["clusters"][idx]["name"] == cluster.name
            assert clusters_data["clusters"][idx]["percent"] == cluster.percent

    @responses.activate
    @pytest.mark.parametrize(
        "status_code,body",
        [
            (422, {"message": "No current cluster with name Cluster 1"}),
            (404, {"message": "Not Found"}),
        ],
    )
    def test_update_multiple_names_error(
        self, cluster_url, project_id, model_id, status_code, body
    ):
        """
        Given error response from api with status_codes (404, 422)
        When I update multiple cluster names
        Then method should raise ClientError
        """
        responses.add(
            responses.PATCH,
            cluster_url,
            status=status_code,
            content_type="application/json",
            body=json.dumps(body),
        )
        mappings = [
            ("old name 1", "new name 1"),
            ("old name 2", "new name 2"),
            ("old name 3", "new name 3"),
        ]
        with pytest.raises(ClientError):
            Cluster.update_multiple_names(project_id, model_id, mappings)
