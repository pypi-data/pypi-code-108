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
import copy
from copy import deepcopy
import json
import os
from shutil import rmtree

import mock
import pytest
from requests_toolbelt import MultipartEncoder
import responses
from trafaret import DataError

from datarobot import errors
from datarobot.enums import DEFAULT_MAX_WAIT
from datarobot.models.custom_model_version import RequiredMetadataValue
from datarobot.models.custom_task_version import CustomTaskFileItem, CustomTaskVersion
from datarobot.utils import camelize, underscorize
from tests.model.utils import (
    assert_custom_task_version,
    assert_custom_task_version_dependency_build,
    assert_items,
    assert_single_api_call,
    change_response_value,
    fields_to_dict,
)


@pytest.fixture
def version_url(unittest_endpoint, custom_task_id, custom_task_version_id):
    return "{}/customTasks/{}/versions/{}/".format(
        unittest_endpoint, custom_task_id, custom_task_version_id
    )


@pytest.fixture
def versions_base_url(unittest_endpoint, custom_task_id):
    return "{}/customTasks/{}/versions/".format(unittest_endpoint, custom_task_id)


@pytest.fixture
def nullable_keys():
    return {
        "description",
        "baseEnvironmentId",
        "baseEnvironmentVersionId",
    }


def add_mock_get_response(url, json_dict):
    add_mock_response(responses.GET, url, json.dumps(json_dict))


def add_mock_response(method, url, body):
    responses.add(method, url, status=200, content_type="application/json", body=body)


@pytest.fixture()
def version_get_response(version_url, custom_task_version_response_json):
    add_mock_get_response(version_url, custom_task_version_response_json)


@pytest.fixture
def dependency_img_build_route(unittest_endpoint, custom_task_id, custom_task_version_id):
    return "{}/customTasks/{}/versions/{}/dependencyBuild/".format(
        unittest_endpoint, custom_task_id, custom_task_version_id,
    )


@pytest.fixture
def dependency_img_build_log_route(unittest_endpoint, custom_task_id, custom_task_version_id):
    return "{}/customTasks/{}/versions/{}/dependencyBuildLog/".format(
        unittest_endpoint, custom_task_id, custom_task_version_id,
    )


FILE_ITEM_RESPONSE_KEYS = [camelize(el.name) for el in CustomTaskFileItem.schema.keys]


class TestCustomTaskFileItem:
    def test_from_server_data_custom_model_file_item(self, workspace_items):
        assert_items(
            [CustomTaskFileItem.from_server_data(el) for el in workspace_items], workspace_items
        )

    @pytest.mark.parametrize("key", FILE_ITEM_RESPONSE_KEYS)
    def test_from_server_data_no_optional_values(self, workspace_items, key):
        """Necessary because the class it inherits from allows created to be nullable."""
        item = workspace_items[0]
        item[key] = None
        with pytest.raises(DataError) as exec_info:
            CustomTaskFileItem.from_server_data(item)
        error = exec_info.value
        assert len(error.error) == 1
        assert error.error[underscorize(key)].error == "is required"


class TestCustomTaskVersionGetActionsAndUpdate:
    def test_from_server_data_minimal_response(self, custom_task_version):
        version = CustomTaskVersion.from_server_data(custom_task_version)
        assert_custom_task_version(version, custom_task_version)

    def test_from_server_data_full_response(self, custom_task_version_with_optional_values):
        version = CustomTaskVersion.from_server_data(custom_task_version_with_optional_values)
        assert_custom_task_version(version, custom_task_version_with_optional_values)

    def test_from_server_data_nullable_values(
        self, custom_task_version_response_json, nullable_keys
    ):
        for key in nullable_keys:
            custom_task_version_response_json[key] = None
        version = CustomTaskVersion.from_server_data(custom_task_version_response_json)
        assert_custom_task_version(version, custom_task_version_response_json)

    @responses.activate
    @pytest.mark.usefixtures("version_get_response")
    def test_get_custom_task_version(self, custom_task_version_response_json):
        task_id = custom_task_version_response_json["customTaskId"]
        version_id = custom_task_version_response_json["id"]
        version = CustomTaskVersion.get(task_id, version_id)
        assert_custom_task_version(version, custom_task_version_response_json)

        assert_single_api_call(
            responses.calls,
            responses.GET,
            "/customTasks/{}/versions/{}/".format(task_id, version_id),
        )

    @responses.activate
    def test_refresh_custom_task_version(self, custom_task_version_response_json, version_url):
        task_id = custom_task_version_response_json["customTaskId"]
        version_id = custom_task_version_response_json["id"]

        updated_response = {
            key: change_response_value(value)
            for key, value in custom_task_version_response_json.items()
        }

        add_mock_get_response(version_url, custom_task_version_response_json)
        add_mock_get_response(version_url, updated_response)

        version = CustomTaskVersion.get(task_id, version_id)

        assert len(responses.calls) == 1
        assert_custom_task_version(version, custom_task_version_response_json)

        version.refresh()

        assert len(responses.calls) == 2
        assert_custom_task_version(version, updated_response)

    @responses.activate
    def test_list_response_single_list(
        self, custom_task_version_list_response, custom_task_id, versions_base_url
    ):
        add_mock_get_response(versions_base_url, custom_task_version_list_response)
        result = CustomTaskVersion.list(custom_task_id)
        assert len(result) == len(custom_task_version_list_response["data"])
        for actual, expected in zip(result, custom_task_version_list_response["data"]):
            assert_custom_task_version(actual, expected)

        assert_single_api_call(
            responses.calls, responses.GET, "/customTasks/{}/versions/".format(custom_task_id)
        )

    @responses.activate
    def test_list_response_multi_list(
        self, custom_task_version_list_response, custom_task_id, versions_base_url
    ):
        next_page = deepcopy(custom_task_version_list_response)
        next_data = next_page["data"]
        for el in next_data:
            for key in el:
                el[key] = change_response_value(el[key])

        next_url = "https://www.coolguy.com/coolness/"
        custom_task_version_list_response["next"] = next_url
        add_mock_get_response(versions_base_url, custom_task_version_list_response)
        add_mock_get_response(next_url, next_page)
        result = CustomTaskVersion.list(custom_task_id)
        assert len(result) == len(custom_task_version_list_response["data"]) * 2
        for actual, expected in zip(result, custom_task_version_list_response["data"] + next_data):
            assert_custom_task_version(actual, expected)

    @responses.activate
    @pytest.mark.usefixtures("version_get_response")
    def test_download(self, temporary_file, version_url, custom_task_id, custom_task_version_id):
        target_url = version_url + "download/"
        content = b"some stuff"
        add_mock_response(responses.GET, target_url, content)
        version = CustomTaskVersion.get(custom_task_id, custom_task_version_id)
        version.download(temporary_file)
        with open(temporary_file, "rb") as f:
            assert f.read() == content

        calls_after_get = responses.calls[1:]
        expected_url = "customTasks/{}/versions/{}/download/".format(
            custom_task_id, custom_task_version_id
        )
        assert_single_api_call(calls_after_get, responses.GET, expected_url)

    @responses.activate
    @pytest.mark.usefixtures("version_get_response")
    def test_update(
        self, version_url, custom_task_id, custom_task_version_id, custom_task_version_response_json
    ):
        updated_json = deepcopy(custom_task_version_response_json)
        updated_json["requiredMetadata"] = {"TEST_UPDATE": "new_value", "otherThing": "OthErValue"}
        updated_json["description"] = "test_update description which is so awesome"

        add_mock_response(responses.PATCH, version_url, body=json.dumps(updated_json))

        version = CustomTaskVersion.get(custom_task_id, custom_task_version_id)
        version.update("dummy_value", {"DUMMY_VALUE": "value"})

        calls_after_get = responses.calls[1:]
        expected_url_ending = "customTasks/{}/versions/{}/".format(
            version.custom_task_id, version.id
        )
        assert_single_api_call(calls_after_get, responses.PATCH, expected_url_ending)

        call = calls_after_get[0]
        assert json.loads(call.request.body) == {
            "description": "dummy_value",
            "requiredMetadata": {"DUMMY_VALUE": "value"},
        }
        assert_custom_task_version(version, updated_json)

    @responses.activate
    @pytest.mark.usefixtures("version_get_response")
    def test_update_only_description(
        self, version_url, custom_task_id, custom_task_version_id, custom_task_version_response_json
    ):
        add_mock_response(
            responses.PATCH, version_url, body=json.dumps(custom_task_version_response_json)
        )

        version = CustomTaskVersion.get(custom_task_id, custom_task_version_id)
        version.update(description="only description")

        call = responses.calls[1]
        assert json.loads(call.request.body) == {"description": "only description"}

    @responses.activate
    @pytest.mark.usefixtures("version_get_response")
    def test_update_with_deprecated_required_metadata(
        self,
        version_url,
        custom_task_id,
        custom_task_version_id,
        custom_task_version_response_json,
    ):
        add_mock_response(
            responses.PATCH, version_url, body=json.dumps(custom_task_version_response_json)
        )

        version = CustomTaskVersion.get(custom_task_id, custom_task_version_id)
        attrs = {"required_metadata": {"hello": "world"}}

        version.update(**attrs)
        call = responses.calls[1]
        assert json.loads(call.request.body) == {"requiredMetadata": {"hello": "world"}}

    @responses.activate
    @pytest.mark.usefixtures("version_get_response")
    def test_update_with_required_metadata_values(
        self,
        version_url,
        custom_task_id,
        custom_task_version_id,
        custom_task_version_response_json,
    ):
        add_mock_response(
            responses.PATCH, version_url, body=json.dumps(custom_task_version_response_json)
        )

        version = CustomTaskVersion.get(custom_task_id, custom_task_version_id)
        attrs = {
            "required_metadata_values": [RequiredMetadataValue(field_name="hello", value="world")]
        }

        version.update(**attrs)
        call = responses.calls[1]
        assert json.loads(call.request.body) == {
            "requiredMetadataValues": [{"fieldName": "hello", "value": "world"}]
        }

    @responses.activate
    @pytest.mark.usefixtures("version_get_response")
    @pytest.mark.parametrize("required_metadata", [{}, {"a": "b"}], ids=["empty", "non-empty"])
    @pytest.mark.parametrize(
        "required_metadata_values",
        [[], [RequiredMetadataValue(field_name="a", value="b")]],
        ids=["empty", "non-empty"],
    )
    def test_update_with_both_required_metadata_and_required_metadata_value_raises_error(
        self, custom_task_id, custom_task_version_id, required_metadata, required_metadata_values
    ):

        version = CustomTaskVersion.get(custom_task_id, custom_task_version_id)
        attrs = {
            "required_metadata_values": required_metadata_values,
            "required_metadata": required_metadata,
        }

        with pytest.raises(ValueError):
            version.update(**attrs)


class TestCreateMethods:
    @staticmethod
    def _get_http_method(create_method):
        if create_method == CustomTaskVersion.create_clean:
            http_method = responses.POST
        else:
            http_method = responses.PATCH
        return http_method

    @responses.activate
    @pytest.mark.parametrize(
        "create_method",
        [CustomTaskVersion.create_clean, CustomTaskVersion.create_from_previous],
        ids=["create_clean", "create_from_previous"],
    )
    def test_minimal_request(
        self, versions_base_url, custom_task_id, custom_task_version_response_json, create_method
    ):

        http_method = self._get_http_method(create_method)

        add_mock_response(
            http_method, versions_base_url, json.dumps(custom_task_version_response_json)
        )

        base_env_id = "abc123"
        response = create_method(custom_task_id, base_env_id)

        assert_single_api_call(
            responses.calls, http_method, "customTasks/{}/versions/".format(custom_task_id)
        )
        assert_custom_task_version(response, custom_task_version_response_json)

        request_body = responses.calls[0].request.body
        assert isinstance(request_body, MultipartEncoder)
        assert fields_to_dict(request_body) == {
            "baseEnvironmentId": [base_env_id],
            "isMajorUpdate": ["True"],
        }

    @responses.activate
    @pytest.mark.parametrize(
        "create_method",
        [CustomTaskVersion.create_clean, CustomTaskVersion.create_from_previous],
        ids=["create_clean", "create_from_previous"],
    )
    @pytest.mark.parametrize("is_major_update", [True, False])
    def test_optional_values_with_deprecated_required_metadata(
        self,
        versions_base_url,
        custom_task_id,
        custom_task_version_response_json,
        create_method,
        is_major_update,
    ):

        http_method = self._get_http_method(create_method)

        add_mock_response(
            http_method, versions_base_url, json.dumps(custom_task_version_response_json)
        )

        maxmem = 1337
        base_env_id = "abc123"
        required_metadata = {"HI_THERE": "stuff"}
        attrs = dict(
            custom_task_id=custom_task_id,
            base_environment_id=base_env_id,
            maximum_memory=maxmem,
            is_major_update=is_major_update,
            required_metadata=required_metadata,
        )
        api_attrs = {
            "baseEnvironmentId": [base_env_id],
            "isMajorUpdate": [str(is_major_update)],
            "requiredMetadata": [json.dumps(required_metadata)],
            "maximumMemory": [str(maxmem)],
        }

        create_method(**attrs)

        request_body = responses.calls[0].request.body
        assert fields_to_dict(request_body) == api_attrs
        assert (
            responses.calls[0]
            .request.headers["Content-Type"]
            .startswith("multipart/form-data; boundary=")
        )

    @responses.activate
    @pytest.mark.parametrize(
        "create_method",
        [CustomTaskVersion.create_clean, CustomTaskVersion.create_from_previous],
        ids=["create_clean", "create_from_previous"],
    )
    @pytest.mark.parametrize("is_major_update", [True, False])
    def test_optional_values_with_required_metadata_values(
        self,
        versions_base_url,
        custom_task_id,
        custom_task_version_response_json,
        create_method,
        is_major_update,
    ):

        http_method = self._get_http_method(create_method)

        add_mock_response(
            http_method, versions_base_url, json.dumps(custom_task_version_response_json)
        )

        base_env_id = "abc123"
        required_metadata = {"HI_THERE": "stuff"}
        attrs = dict(
            custom_task_id=custom_task_id,
            base_environment_id=base_env_id,
            is_major_update=is_major_update,
            required_metadata_values=[
                RequiredMetadataValue(field_name=k, value=v) for k, v in required_metadata.items()
            ],
        )
        api_attrs = {
            "baseEnvironmentId": [base_env_id],
            "isMajorUpdate": [str(is_major_update)],
            "requiredMetadataValues": [
                json.dumps(
                    [
                        {camelize(k): v for k, v in val.to_dict().items()}
                        for val in attrs["required_metadata_values"]
                    ]
                )
            ],
        }

        create_method(**attrs)

        request_body = responses.calls[0].request.body
        assert fields_to_dict(request_body) == api_attrs
        assert (
            responses.calls[0]
            .request.headers["Content-Type"]
            .startswith("multipart/form-data; boundary=")
        )

    @pytest.mark.parametrize(
        "create_method",
        [CustomTaskVersion.create_clean, CustomTaskVersion.create_from_previous],
        ids=["create_clean", "create_from_previous"],
    )
    @pytest.mark.parametrize("required_metadata", [{}, {"a": "b"}], ids=["empty", "non-empty"])
    @pytest.mark.parametrize(
        "required_metadata_values",
        [[], [RequiredMetadataValue(field_name="a", value="b")]],
        ids=["empty", "non-empty"],
    )
    def test_optional_values_with_both_required_metadata_and_required_metadata_value_raises_error(
        self, create_method, required_metadata, required_metadata_values
    ):

        attrs = dict(
            custom_task_id="def456",
            base_environment_id="abc123",
            required_metadata_values=required_metadata_values,
            required_metadata=required_metadata,
        )

        with pytest.raises(ValueError):
            create_method(**attrs)

    @responses.activate
    @pytest.mark.parametrize(
        "create_method",
        [CustomTaskVersion.create_clean, CustomTaskVersion.create_from_previous],
        ids=["create_clean", "create_from_previous"],
    )
    def test_file_path(
        self,
        temporary_dir,
        versions_base_url,
        custom_task_id,
        custom_task_version_response_json,
        create_method,
    ):
        top_file_name = "a-file.txt"
        sub_file_name = "sub-file.txt"
        top_file_path = os.path.join(temporary_dir, top_file_name)
        sub_file_path = os.path.join(temporary_dir, "sub-dir", sub_file_name)

        os.mkdir(os.path.dirname(sub_file_path))

        for file_name in (top_file_path, sub_file_path):
            with open(file_name, "wb") as f:
                f.write(b"some content")

        http_method = self._get_http_method(create_method)
        add_mock_response(
            http_method, versions_base_url, json.dumps(custom_task_version_response_json)
        )

        create_method(custom_task_id, "abc", folder_path=temporary_dir)

        fields = fields_to_dict(responses.calls[0].request.body)

        files = fields["file"]
        paths = fields["filePath"]

        parent_dir_size = len(temporary_dir + "/")
        relative_paths = {
            top_file_name: top_file_path[parent_dir_size:],
            sub_file_name: sub_file_path[parent_dir_size:],
        }
        for (filename, file_obj), file_path in zip(files, paths):
            assert relative_paths[filename] == file_path
            assert file_obj.closed

    @responses.activate
    @pytest.mark.parametrize(
        "create_method",
        [CustomTaskVersion.create_clean, CustomTaskVersion.create_from_previous],
        ids=["create_clean", "create_from_previous"],
    )
    def test_bad_file_path_raises_value_error(
        self,
        temporary_dir,
        versions_base_url,
        custom_task_id,
        custom_task_version_response_json,
        create_method,
    ):
        garbage_file_path = os.path.join(temporary_dir, "garbage_dir")
        rmtree(garbage_file_path, ignore_errors=True)

        assert not os.path.exists(garbage_file_path)

        http_method = self._get_http_method(create_method)
        add_mock_response(
            http_method, versions_base_url, json.dumps(custom_task_version_response_json)
        )

        with pytest.raises(ValueError):
            create_method(custom_task_id, "abc", folder_path=garbage_file_path)

    @responses.activate
    def test_create_from_previous_files_to_delete(
        self, versions_base_url, custom_task_id, custom_task_version_response_json,
    ):
        add_mock_response(
            responses.PATCH, versions_base_url, json.dumps(custom_task_version_response_json)
        )

        CustomTaskVersion.create_from_previous(
            custom_task_id, "abc123", files_to_delete=["abc", "def"]
        )
        fields = fields_to_dict(responses.calls[0].request.body)
        assert set(fields["filesToDelete"]) == {"abc", "def"}
        assert len(fields["filesToDelete"]) == 2


class TestDependencyImageBuild:
    @responses.activate
    def test_start_dependency_build__no_waiting(
        self,
        dependency_img_build_route,
        custom_task_version,
        custom_task_version_dependency_build_server_data,
    ):
        version = CustomTaskVersion.from_server_data(custom_task_version)
        responses.add(
            responses.POST,
            dependency_img_build_route,
            status=202,
            content_type="application/json",
            json=custom_task_version_dependency_build_server_data,
        )

        dependency_build = version.start_dependency_build()
        assert len(responses.calls) == 1
        assert_custom_task_version_dependency_build(
            dependency_build, custom_task_version_dependency_build_server_data
        )

    @responses.activate
    def test_start_dependency_build__with_waiting(
        self,
        dependency_img_build_route,
        custom_task_version,
        custom_task_version_dependency_build_server_data,
    ):
        version = CustomTaskVersion.from_server_data(custom_task_version)
        # simulate the response of starting a dependency image build
        response_data = copy.copy(custom_task_version_dependency_build_server_data)
        responses.add(
            responses.POST,
            dependency_img_build_route,
            status=202,
            content_type="application/json",
            json=response_data,
        )
        # simulate the 1st pull of status
        response_data = copy.copy(custom_task_version_dependency_build_server_data)
        response_data["buildStatus"] = "processing"
        responses.add(
            responses.GET,
            dependency_img_build_route,
            status=200,
            content_type="application/json",
            json=response_data,
        )
        # simulate the 2nd pull of status
        response_data = copy.copy(custom_task_version_dependency_build_server_data)
        response_data["buildStatus"] = "success"
        responses.add(
            responses.GET,
            dependency_img_build_route,
            status=200,
            content_type="application/json",
            json=response_data,
        )

        with mock.patch("time.sleep"):
            dependency_build = version.start_dependency_build_and_wait(max_wait=DEFAULT_MAX_WAIT)
        assert len(responses.calls) == 3
        # check the final response
        assert_custom_task_version_dependency_build(dependency_build, response_data)

    @responses.activate
    def test_start_dependency_build__raise_timeout_error(
        self,
        dependency_img_build_route,
        custom_task_version,
        custom_task_version_dependency_build_server_data,
    ):
        version = CustomTaskVersion.from_server_data(custom_task_version)
        # simulate the response of starting a dependency image build
        response_data = custom_task_version_dependency_build_server_data
        responses.add(
            responses.POST,
            dependency_img_build_route,
            status=202,
            content_type="application/json",
            json=response_data,
        )
        # simulate the pull of status
        response_data["buildStatus"] = "processing"
        responses.add(
            responses.GET,
            dependency_img_build_route,
            status=200,
            content_type="application/json",
            json=response_data,
        )

        with mock.patch("time.sleep"):
            with pytest.raises(errors.AsyncTimeoutError):
                version.start_dependency_build_and_wait(max_wait=0)

    @responses.activate
    def test_get_dependency_build(
        self,
        dependency_img_build_route,
        custom_task_version,
        custom_task_version_dependency_build_server_data,
    ):
        version = CustomTaskVersion.from_server_data(custom_task_version)
        response_data = custom_task_version_dependency_build_server_data
        responses.add(
            responses.GET,
            dependency_img_build_route,
            status=200,
            content_type="application/json",
            json=response_data,
        )
        build_info = version.get_dependency_build()
        assert len(responses.calls) == 1
        assert_custom_task_version_dependency_build(build_info, response_data)

    @responses.activate
    @pytest.mark.parametrize("file_directory", [False, "file_directory"])
    def test_download_dependency_build_log(
        self, file_directory, dependency_img_build_log_route, custom_task_version, tmpdir,
    ):
        version = CustomTaskVersion.from_server_data(custom_task_version)
        responses.add(
            responses.GET,
            dependency_img_build_log_route,
            status=200,
            body="body",
            headers={"Content-Disposition": "attachment; filename=default_filename"},
        )

        downloaded_file = tmpdir.mkdir(file_directory) if file_directory else tmpdir
        version.download_dependency_build_log(file_directory=str(downloaded_file))
        assert len(responses.calls) == 1
        downloaded_file = (
            tmpdir.join(file_directory, "default_filename")
            if file_directory
            else tmpdir.join("default_filename")
        )
        assert downloaded_file.read() == "body"

    @responses.activate
    def test_cancel_dependency_build(self, dependency_img_build_route, custom_task_version):
        version = CustomTaskVersion.from_server_data(custom_task_version)
        responses.add(responses.DELETE, dependency_img_build_route, status=204)

        version.cancel_dependency_build()

        assert len(responses.calls) == 1
