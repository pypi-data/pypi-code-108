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

import datarobot as dr
from datarobot.utils import camelize
from tests.utils import request_body_to_json


class TestHDFSCreate(object):
    @pytest.fixture
    def hdfs_create_response(self, unittest_endpoint, async_url):
        mysql_create_url = "{}/{}/".format(unittest_endpoint, "hdfsProjects")
        responses.add(
            responses.POST,
            mysql_create_url,
            body="",
            status=202,
            content_type="application/json",
            adding_headers={"Location": async_url},
        )

    @responses.activate
    @pytest.mark.usefixtures("project_creation_responses", "hdfs_create_response")
    def test_create_hdfs_minimum(self):
        dr.Project.create_from_hdfs(url="hdfs://webhdfs.com/directory/file.csv")
        create_body = request_body_to_json(responses.calls[0].request)
        assert create_body["url"] == "hdfs://webhdfs.com/directory/file.csv"

    @responses.activate
    @pytest.mark.usefixtures("project_creation_responses", "hdfs_create_response")
    def test_create_hdfs_all_options(self):
        dr.Project.create_from_hdfs(
            url="hdfs://webhdfs.com/directory/file.csv",
            port=9999,
            project_name="HDFS Project",
            max_wait=100,
        )
        create_body = request_body_to_json(responses.calls[0].request)
        assert create_body["url"] == "hdfs://webhdfs.com/directory/file.csv"
        assert create_body["port"] == 9999
        assert create_body["projectName"] == "HDFS Project"


class TestDataSourceCreate(object):
    @pytest.fixture
    def data_source_create_response(self, unittest_endpoint, async_url):
        project_create_url = "{}/{}".format(unittest_endpoint, dr.Project._path)
        responses.add(
            responses.POST,
            project_create_url,
            body="",
            status=202,
            content_type="application/json",
            adding_headers={"Location": async_url},
        )

    @pytest.fixture
    def data_source(self):
        return dr.DataSource("5acc8437ec8d670001ba16bf")

    @responses.activate
    @pytest.mark.usefixtures("project_creation_responses", "data_source_create_response")
    def test_create_from_data_source_id(self):
        username = "test_user"
        password = "megasuperubersecretpassword"
        data_source_id = "5acc8437ec8d670001ba16bf"
        project_name = "data source project"
        dr.Project.create_from_data_source(
            data_source_id, username, password, project_name=project_name
        )
        create_body = request_body_to_json(responses.calls[0].request)
        assert create_body == {
            "user": username,
            "password": password,
            "dataSourceId": data_source_id,
            "projectName": project_name,
        }


class TestDatasetCreate(object):
    @responses.activate
    @pytest.mark.usefixtures("project_creation_responses")
    def test_create_from_dataset_use_defaults(
        self, project_collection_url, project_without_target_json
    ):
        dataset_id = "abc123"
        project = dr.Project.create_from_dataset(dataset_id)

        create_body = request_body_to_json(responses.calls[0].request)
        assert create_body == {"datasetId": dataset_id}
        assert responses.calls[0].request.url == project_collection_url

        response_json = json.loads(project_without_target_json)
        assert project.id == response_json["id"]
        assert project.project_name == response_json["projectName"]
        assert project.file_name == response_json["fileName"]
        assert project.stage == response_json["stage"]

    @responses.activate
    @pytest.mark.usefixtures("project_creation_responses")
    @pytest.mark.parametrize(
        "param_name,param_value",
        [
            ("dataset_version_id", "20gjkfdlj"),
            ("project_name", "my cool name"),
            ("user", "that guy over there"),
            ("password", "my voice is my passport"),
            ("credential_id", "12345"),
            ("use_kerberos", True),
        ],
    )
    def test_create_from_dataset_using_params(self, param_name, param_value):
        dataset_id = "abc123"
        dr.Project.create_from_dataset(dataset_id, **{param_name: param_value})
        create_body = request_body_to_json(responses.calls[0].request)
        assert create_body == {"datasetId": dataset_id, camelize(param_name): param_value}
