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

from datarobot.errors import (
    AsyncFailureError,
    AsyncProcessUnsuccessfulError,
    AsyncTimeoutError,
    ClientError,
)
from datarobot.models import ClusterInsight
from datarobot.utils import from_api


class TestClusterInsight(object):
    def assert_equal(self, cluster_insight, dict_data):
        assert cluster_insight.feature_name == dict_data["featureName"]
        assert cluster_insight.feature_type == dict_data["featureType"]
        assert cluster_insight.feature_impact == dict_data["featureImpact"]
        assert len(cluster_insight.insights) == len(dict_data["insights"])

    def test_numeric_instantiation(self, cluster_insights_numeric_feature):
        """
        Given numeric cluster insight
        When ClusterInsight gets instantiated
        Then data in instance should match data source
        """
        cl = ClusterInsight.from_data(from_api(cluster_insights_numeric_feature))
        self.assert_equal(cl, cluster_insights_numeric_feature)

    def test_categorical_instantiation(self, cluster_insights_categorical_feature):
        """
        Given categorical cluster insight
        When ClusterInsight gets instantiated
        Then data in instance should match data source
        """
        cl = ClusterInsight.from_data(from_api(cluster_insights_categorical_feature))
        self.assert_equal(cl, cluster_insights_categorical_feature)

    def test_image_instantiation(self, cluster_insights_image_feature):
        """
        Given image cluster insight
        When ClusterInsight gets instantiated
        Then data in instance should match data source
        """
        cl = ClusterInsight.from_data(from_api(cluster_insights_image_feature))
        self.assert_equal(cl, cluster_insights_image_feature)

    def test_text_instantiation(self, cluster_insights_text_feature):
        """
        Given text cluster insight
        When ClusterInsight gets instantiated
        Then data in instance should match data source
        """
        cl = ClusterInsight.from_data(from_api(cluster_insights_text_feature))
        self.assert_equal(cl, cluster_insights_text_feature)

    def test_geospatial_instantiation(self, cluster_insights_geospatial_feature):
        """
        Given geospatial cluster insight
        When ClusterInsight gets instantiated
        Then data in instance should match data source
        """
        cl = ClusterInsight.from_data(from_api(cluster_insights_geospatial_feature))
        self.assert_equal(cl, cluster_insights_geospatial_feature)

    @responses.activate
    def test_cluster_insights_list_ok(
        self, cluster_insights_data, cluster_insights_url, project_id, model_id
    ):
        """
        Given correct api response
        When listing ClusterInsights
        Then data and order of insights should match api response
        """
        responses.add(
            responses.GET,
            cluster_insights_url,
            status=200,
            content_type="application/json",
            body=json.dumps(cluster_insights_data),
        )
        cl = ClusterInsight.list(project_id, model_id)
        data = cluster_insights_data["data"]
        assert len(cl) == len(data)
        for cl, data in zip(cl, data):
            self.assert_equal(cl, data)

    @responses.activate
    @pytest.mark.parametrize(
        "status_code,body",
        [
            (404, {"message": "There are no cluster insights available for this model yet."}),
            (404, {"message": "Not Found"}),
        ],
    )
    def test_cluster_insights_list_error(
        self, cluster_insights_url, project_id, model_id, status_code, body
    ):
        """
        Given error api response status_code (404) with various messages
        When listing ClusterInsights
        Then method should raise ClientError
        """
        responses.add(
            responses.GET,
            cluster_insights_url,
            status=404,
            content_type="application/json",
            body=json.dumps(body),
        )
        with pytest.raises(ClientError):
            ClusterInsight.list(project_id, model_id)

    @responses.activate
    def test_cluster_insights_compute_error_job_max_time_timeout(
        self, cluster_insights_url, job_url, project_id, model_id
    ):
        """
        Given valid api responses with not finished processing till max_time
        When listing ClusterInsights
        Then method should raise AsyncTimeoutError
        """
        responses.add(
            responses.POST,
            cluster_insights_url,
            adding_headers={"Location": job_url},
            status=200,
            content_type="application/json",
            body="",
        )

        job_mock = {
            "id": "1",
            "projectId": project_id,
            "status": "inprogress",
            "jobType": "clusterInsights",
            "isBlocked": False,
            "url": job_url,
            "modelId": model_id,
        }

        responses.add(
            responses.GET,
            job_url,
            content_type="application/json",
            status=200,
            body=json.dumps(job_mock),
        )

        with pytest.raises(AsyncTimeoutError):
            ClusterInsight.compute(project_id, model_id, max_wait=1)

    @responses.activate
    def test_cluster_insights_compute_error_job_aborted(
        self, cluster_insights_url, job_url, project_id, model_id
    ):
        """
        Given clusterInsights computing job was aborted
        When listing ClusterInsights
        Then method should raise AsyncProcessUnsuccessfulError
        """
        responses.add(
            responses.POST,
            cluster_insights_url,
            adding_headers={"Location": job_url},
            status=200,
            content_type="application/json",
            body="",
        )

        job_mock = {
            "id": "1",
            "projectId": project_id,
            "status": "ABORTED",
            "jobType": "clusterInsights",
            "isBlocked": False,
            "url": job_url,
            "modelId": model_id,
        }

        responses.add(
            responses.GET,
            job_url,
            content_type="application/json",
            status=200,
            body=json.dumps(job_mock),
        )

        with pytest.raises(AsyncProcessUnsuccessfulError):
            ClusterInsight.compute(project_id, model_id, max_wait=1)

    @responses.activate
    def test_cluster_insights_compute_error_unexpected_status_code(
        self, cluster_insights_url, job_url, project_id, model_id
    ):
        """
        Given unexpected api response from job_status (code other than 200, 303
        When listing ClusterInsights
        Then method should raise AsyncProcessUnsuccessfulError
        """
        responses.add(
            responses.POST,
            cluster_insights_url,
            adding_headers={"Location": job_url},
            status=200,
            content_type="application/json",
            body="",
        )

        job_mock = {
            "id": "1",
            "projectId": project_id,
            "status": "ABORTED",
            "jobType": "clusterInsights",
            "isBlocked": False,
            "url": job_url,
            "modelId": model_id,
        }

        responses.add(
            responses.GET,
            job_url,
            content_type="application/json",
            status=301,
            body=json.dumps(job_mock),
        )

        with pytest.raises(AsyncFailureError):
            ClusterInsight.compute(project_id, model_id, max_wait=1)

    @responses.activate
    def test_cluster_insights_compute_ok(
        self, cluster_insights_url, job_url, cluster_insights_data, project_id, model_id
    ):
        """
        Given valid computation of clusterInsights
        When listing ClusterInsights
        Then method should return ClusterInsights with same order and data to api response
        """
        responses.add(
            responses.POST,
            cluster_insights_url,
            adding_headers={"Location": job_url},
            status=200,
            content_type="application/json",
            body="",
        )
        responses.add(
            responses.GET,
            job_url,
            content_type="application/json",
            status=303,
            adding_headers={"Location": cluster_insights_url},
        )
        responses.add(
            responses.GET,
            cluster_insights_url,
            status=200,
            content_type="application/json",
            body=json.dumps(cluster_insights_data),
        )
        cl = ClusterInsight.compute(project_id, model_id)
        data = cluster_insights_data["data"]
        assert len(cl) == len(data)
        for cl, data in zip(cl, data):
            self.assert_equal(cl, data)
