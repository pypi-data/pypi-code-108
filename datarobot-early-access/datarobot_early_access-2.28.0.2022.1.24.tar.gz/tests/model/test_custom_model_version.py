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
from collections import defaultdict
from copy import deepcopy
import json
import os
import uuid

import mock
import pytest
from requests_toolbelt import MultipartEncoder
import responses
import six

from datarobot import CustomModelVersion
from datarobot.models.custom_model_version import RequiredMetadataValue
from datarobot.utils import camelize
from tests.model.utils import assert_custom_model_version, fields_to_dict


@pytest.fixture
def mocked_version(mocked_custom_model_version):
    return mocked_custom_model_version


@pytest.fixture
def mocked_version_with_resources(mocked_custom_model_version_with_resources):
    return mocked_custom_model_version_with_resources


@pytest.fixture
def make_versions_url(unittest_endpoint):
    def _make_versions_url(environment_id, version_id=None):
        base_url = "{}/customModels/{}/versions/".format(unittest_endpoint, environment_id)
        if version_id is not None:
            return "{}{}/".format(base_url, version_id)
        return base_url

    return _make_versions_url


def mock_get_response(url, response):
    responses.add(
        responses.GET, url, status=200, content_type="application/json", body=json.dumps(response),
    )


def test_from_server_data(mocked_version):
    version = CustomModelVersion.from_server_data(mocked_version)
    assert_custom_model_version(version, mocked_version)


@responses.activate
@pytest.mark.parametrize(
    "version_json",
    [
        "mocked_version",
        "mocked_custom_model_version_no_dependencies",
        "mocked_custom_model_version_no_base_environment",
        "mocked_custom_model_version_future_field_in_version",
        "mocked_custom_model_version_future_field_in_dependency",
        "mocked_custom_model_version_future_field_in_constraint",
        "mocked_custom_model_version_with_required_metadata",
    ],
)
def test_get_version(request, version_json, make_versions_url):
    # arrange
    version_json = request.getfixturevalue(version_json)
    url = make_versions_url(version_json["customModelId"], version_json["id"])
    mock_get_response(url, version_json)

    # act
    version = CustomModelVersion.get(version_json["customModelId"], version_json["id"])

    # assert
    assert_custom_model_version(version, version_json)

    assert responses.calls[0].request.method == "GET"
    assert responses.calls[0].request.url == url


@responses.activate
def test_list_versions(mocked_versions, make_versions_url):
    # arrange
    custom_model_id = mocked_versions["data"][0]["customModelId"]
    url = make_versions_url(custom_model_id)
    mock_get_response(url, mocked_versions)

    # act
    versions = CustomModelVersion.list(custom_model_id)

    # assert
    assert len(versions) == len(mocked_versions["data"])
    for version, mocked_version in zip(versions, mocked_versions["data"]):
        assert_custom_model_version(version, mocked_version)

    assert responses.calls[0].request.method == "GET"
    assert responses.calls[0].request.url == url


@responses.activate
def test_list_versions_multiple_pages(mocked_versions, make_versions_url):
    # arrange
    custom_model_id = mocked_versions["data"][0]["customModelId"]

    url1 = make_versions_url(custom_model_id)
    url2 = make_versions_url(custom_model_id) + "2"

    mocked_versions_2nd = deepcopy(mocked_versions)
    mocked_versions["next"] = url2

    mock_get_response(url1, mocked_versions)
    mock_get_response(url2, mocked_versions_2nd)

    # act
    versions = CustomModelVersion.list(custom_model_id)

    # assert
    assert len(versions) == len(mocked_versions["data"]) + len(mocked_versions_2nd["data"])
    for version, mocked_version in zip(
        versions, mocked_versions["data"] + mocked_versions_2nd["data"]
    ):
        assert_custom_model_version(version, mocked_version)

    assert responses.calls[0].request.method == "GET"
    assert responses.calls[0].request.url == url1
    assert responses.calls[1].request.method == "GET"
    assert responses.calls[1].request.url == url2


@responses.activate
def test_download(mocked_version, make_versions_url, tmpdir):
    # arrange
    url = make_versions_url(mocked_version["customModelId"], mocked_version["id"])
    mock_get_response(url, mocked_version)
    responses.add(
        responses.GET,
        url + "download/",
        status=200,
        content_type="application/json",
        body=b"content",
    )

    downloaded_file = tmpdir.mkdir("sub").join("download")
    downloaded_file_path = str(downloaded_file)

    # act
    version = CustomModelVersion.get(mocked_version["customModelId"], mocked_version["id"])
    version.download(downloaded_file_path)

    # assert
    assert six.ensure_binary(downloaded_file.read()) == b"content"

    assert responses.calls[0].request.method == "GET"
    assert responses.calls[0].request.url == url
    assert responses.calls[1].request.method == "GET"
    assert responses.calls[1].request.url == url + "download/"


@responses.activate
@pytest.mark.parametrize("use_deprecated_metadata", [True, False])
def test_update(
    mocked_custom_model_version_with_required_metadata, make_versions_url, use_deprecated_metadata,
):
    mocked_version = mocked_custom_model_version_with_required_metadata
    # arrange
    attrs = {"description": "xx"}
    if use_deprecated_metadata:
        attrs.update({"required_metadata": {"REQUIRED_FIELD": "super important value"}})
    else:
        attrs.update(
            {
                "required_metadata_values": [
                    RequiredMetadataValue(
                        field_name="REQUIRED_FIELD", value="super important value"
                    )
                ]
            }
        )
    api_attrs = {camelize(k): v for k, v in attrs.items()}

    if not use_deprecated_metadata:
        api_attrs["requiredMetadataValues"] = [
            {camelize(k): v for k, v in val.to_dict().items()}
            for val in attrs["required_metadata_values"]
        ]

    url = make_versions_url(mocked_version["customModelId"], mocked_version["id"])
    mock_get_response(url, mocked_version)

    mocked_version.update(api_attrs)

    responses.add(
        responses.PATCH,
        url,
        status=200,
        content_type="application/json",
        body=json.dumps(mocked_version),
    )

    # act
    version = CustomModelVersion.get(mocked_version["customModelId"], mocked_version["id"])
    version.update(**attrs)

    # assert
    assert_custom_model_version(version, mocked_version)

    assert responses.calls[0].request.method == "GET"
    assert responses.calls[0].request.url == url
    assert responses.calls[1].request.method == "PATCH"
    assert responses.calls[1].request.url == url
    assert responses.calls[1].request.body == json.dumps(api_attrs).encode()


@responses.activate
@pytest.mark.parametrize("required_metadata", [{}, {"a": "b"}], ids=["empty", "non-empty"])
@pytest.mark.parametrize(
    "required_metadata_values",
    [[], [RequiredMetadataValue(field_name="a", value="b")]],
    ids=["empty", "non-empty"],
)
def test_update_with_both_required_metadata_and_required_metadata_value_raises_error(
    mocked_custom_model_version_with_required_metadata,
    make_versions_url,
    required_metadata,
    required_metadata_values,
):
    mocked_version = mocked_custom_model_version_with_required_metadata
    # arrange
    attrs = {
        "description": "xx",
        "required_metadata": required_metadata,
        "required_metadata_values": required_metadata_values,
    }

    url = make_versions_url(mocked_version["customModelId"], mocked_version["id"])
    mock_get_response(url, mocked_version)

    # act
    version = CustomModelVersion.get(mocked_version["customModelId"], mocked_version["id"])
    with pytest.raises(ValueError):
        version.update(**attrs)


@responses.activate
def test_refresh(mocked_version, make_versions_url):
    # arrange
    url = make_versions_url(mocked_version["customModelId"], mocked_version["id"])
    mock_get_response(url, mocked_version)

    mocked_version.update({"description": "xx"})

    mock_get_response(url, mocked_version)

    # act
    version = CustomModelVersion.get(mocked_version["customModelId"], mocked_version["id"])
    version.refresh()

    # assert
    assert_custom_model_version(version, mocked_version)

    assert responses.calls[0].request.method == "GET"
    assert responses.calls[0].request.url == url
    assert responses.calls[1].request.method == "GET"
    assert responses.calls[1].request.url == url


@responses.activate
@pytest.mark.parametrize(
    "mocked_fixture_name",
    [
        "mocked_version",
        "mocked_version_with_resources",
        "mocked_custom_model_version_with_required_metadata",
    ],
)
@pytest.mark.parametrize("use_deprecated_metadata", [True, False])
def test_create_clean(
    request,
    mocked_fixture_name,
    make_versions_url,
    tmpdir,
    base_environment_id,
    use_deprecated_metadata,
):
    mocked_version = request.getfixturevalue(mocked_fixture_name)

    url = make_versions_url(mocked_version["customModelId"])

    responses.add(
        responses.POST,
        make_versions_url(mocked_version["customModelId"]),
        status=200,
        content_type="application/json",
        body=json.dumps(mocked_version),
    )

    file = tmpdir.mkdir("sub").join("file.txt")
    file.write(b"content")
    file_path = str(file)

    attrs = dict(
        custom_model_id=mocked_version["customModelId"],
        base_environment_id=base_environment_id,
        is_major_update=True,
        files=[(file_path, "/d/file.txt")],
        network_egress_policy=mocked_version["networkEgressPolicy"],
        maximum_memory=mocked_version["maximumMemory"],
        replicas=mocked_version["replicas"],
    )
    api_attrs = {
        "baseEnvironmentId": [base_environment_id],
        "isMajorUpdate": [str(True)],
        "file": [(os.path.basename(file_path), mock.ANY)],
        "filePath": ["/d/file.txt"],
    }

    if mocked_version["networkEgressPolicy"]:
        api_attrs["networkEgressPolicy"] = [mocked_version["networkEgressPolicy"]]
    if mocked_version["maximumMemory"]:
        api_attrs["maximumMemory"] = [str(mocked_version["maximumMemory"])]
    if mocked_version["replicas"]:
        api_attrs["replicas"] = [str(mocked_version["replicas"])]

    if mocked_version.get("requiredMetadata"):
        if use_deprecated_metadata:
            attrs.update({"required_metadata": mocked_version.get("requiredMetadata")})
            api_attrs.update(
                {"requiredMetadata": [json.dumps(mocked_version.get("requiredMetadata"))]}
            )
        else:
            attrs.update(
                {
                    "required_metadata_values": [
                        RequiredMetadataValue.from_server_data(val)
                        for val in mocked_version.get("requiredMetadataValues")
                    ]
                }
            )
            api_attrs.update(
                {
                    "requiredMetadataValues": [
                        json.dumps(mocked_version.get("requiredMetadataValues"))
                    ],
                }
            )

    version = CustomModelVersion.create_clean(**attrs)
    assert_custom_model_version(version, mocked_version)

    assert responses.calls[0].request.method == "POST"
    assert responses.calls[0].request.url == url
    request_body = responses.calls[0].request.body
    field_dict = fields_to_dict(request_body)
    field_dict["file"] = [(path, mock.ANY) for path, _ in field_dict["file"]]
    assert field_dict == api_attrs


@pytest.mark.parametrize("required_metadata", [{}, {"a": "b"}], ids=["empty", "non-empty"])
@pytest.mark.parametrize(
    "required_metadata_values",
    [[], [RequiredMetadataValue(field_name="a", value="b")]],
    ids=["empty", "non-empty"],
)
def test_create_clean_with_both_required_metadata_and_required_metadata_value_raises_error(
    required_metadata, required_metadata_values
):
    attrs = dict(
        custom_model_id="abc123",
        base_environment_id="dev456",
        is_major_update=True,
        required_metadata=required_metadata,
        required_metadata_values=required_metadata_values,
    )

    with pytest.raises(ValueError):
        CustomModelVersion.create_clean(**attrs)


@responses.activate
def test_create_from_previous(mocked_version, make_versions_url, tmpdir, base_environment_id):
    url = make_versions_url(mocked_version["customModelId"])

    responses.add(
        responses.PATCH,
        make_versions_url(mocked_version["customModelId"]),
        status=200,
        content_type="application/json",
        body=json.dumps(mocked_version),
    )

    file = tmpdir.mkdir("sub").join("file")
    file.write(b"content")
    file_path = str(file)

    version = CustomModelVersion.create_from_previous(
        mocked_version["customModelId"],
        base_environment_id,
        True,
        files=[(file_path, "/d/file.txt")],
        files_to_delete=["2323423423423423"],
    )
    assert_custom_model_version(version, mocked_version)

    assert responses.calls[0].request.method == "PATCH"
    assert responses.calls[0].request.url == url


@responses.activate
@pytest.mark.parametrize(
    "method",
    [
        (CustomModelVersion.create_clean, "POST"),
        (CustomModelVersion.create_from_previous, "PATCH"),
    ],
)
@pytest.mark.parametrize(
    "expected_folder_paths",
    [None, [], ["a.zip", "a/a.zip", "sub/a.txt", "sub/b.pdf", "sub/sub2/c.rtf"]],
)
@pytest.mark.parametrize("expected_file_paths", [None, [], ["y.xyz", "dd/ttt.txt"]])
def test_create_folder_and_files(
    mocked_version,
    make_versions_url,
    tmpdir,
    method,
    expected_folder_paths,
    expected_file_paths,
    base_environment_id,
):
    custom_model_version_method = method[0]
    http_method = method[1]

    # arrange
    responses.add(
        http_method,
        make_versions_url(mocked_version["customModelId"]),
        status=200,
        body=json.dumps(mocked_version),
    )

    # arrange: create folder with required structure to be uploaded
    folder_path = None
    if expected_folder_paths:
        folder_path = tmpdir.mkdir(str(uuid.uuid4()))
        for expected_path in expected_folder_paths:
            path_items, file = os.path.split(expected_path)
            d = folder_path
            if path_items:
                for path_item in path_items.split("/"):
                    if os.path.exists(os.path.join(str(d), path_item)):
                        d = d.join(path_item)
                    else:
                        d = d.mkdir(path_item)
            d.join(file).write(b"content")
        folder_path = str(folder_path)

    # arrange: create files to be uploaded
    files = None
    if expected_file_paths:
        files = []
        for expected_path in expected_file_paths:
            file = tmpdir.join(str(uuid.uuid4()))
            file.write(b"content")
            files.append((str(file), expected_path))

    # act
    custom_model_version_method(
        mocked_version["customModelId"],
        base_environment_id,
        True,
        folder_path=folder_path,
        files=files,
    )

    # assert
    req = responses.calls[0].request
    assert req.method == http_method
    assert req.url == make_versions_url(mocked_version["customModelId"])
    assert isinstance(req.body, MultipartEncoder)

    # get fields submitted with request
    fields = defaultdict(list)
    for name, value in req.body.fields:
        fields[name].append(value)

    assert len(fields["isMajorUpdate"]) == 1
    assert fields["isMajorUpdate"][0] == "True"

    files = fields["file"]
    file_paths = fields["filePath"]

    # verify that files & filePaths make pairs
    assert len(files) == len(file_paths)
    for file, file_path in zip(files, file_paths):
        assert file[0] == os.path.basename(file_path)

    expected_folder_paths = expected_folder_paths or []
    expected_file_paths = expected_file_paths or []

    # There's an option to create a custom model version by passing a pass to a directory.
    # For such a directory, files are created with expected_folder_paths.
    # As there's no control in what order filesystem reads files from a such a directory,
    # convert paths to set and then assert
    assert set(file_paths) == set(expected_folder_paths) | set(expected_file_paths)


@responses.activate
def test_get_feature_impact(mocked_version, make_versions_url, feature_impact_server_data):
    # arrange
    url = make_versions_url(mocked_version["customModelId"], mocked_version["id"])
    mock_get_response(url, mocked_version)
    responses.add(
        responses.GET,
        url + "featureImpact/",
        status=200,
        content_type="application/json",
        body=json.dumps(feature_impact_server_data),
    )

    # act
    image = CustomModelVersion.get(mocked_version["customModelId"], mocked_version["id"])
    feature_impacts = image.get_feature_impact()

    # assert
    assert feature_impacts == feature_impact_server_data["featureImpacts"]

    assert responses.calls[0].request.method == "GET"
    assert responses.calls[0].request.url == url
    assert responses.calls[1].request.method == "GET"
    assert responses.calls[1].request.url == url + "featureImpact/"


@responses.activate
def test_get_feature_impact_with_metadata(
    mocked_version,
    make_versions_url,
    feature_impact_server_data,
    feature_impact_server_data_filtered,
):
    # arrange
    url = make_versions_url(mocked_version["customModelId"], mocked_version["id"])
    mock_get_response(url, mocked_version)
    responses.add(
        responses.GET,
        url + "featureImpact/",
        status=200,
        content_type="application/json",
        body=json.dumps(feature_impact_server_data),
    )

    # act
    image = CustomModelVersion.get(mocked_version["customModelId"], mocked_version["id"])
    feature_impacts = image.get_feature_impact(with_metadata=True)

    # assert
    assert feature_impacts == feature_impact_server_data_filtered

    assert responses.calls[0].request.method == "GET"
    assert responses.calls[0].request.url == url
    assert responses.calls[1].request.method == "GET"
    assert responses.calls[1].request.url == url + "featureImpact/"


@responses.activate
def test_calculate_feature_impact(unittest_endpoint, mocked_version, make_versions_url):
    # arrange
    status_url = "{}/status_url".format(unittest_endpoint)
    url = make_versions_url(mocked_version["customModelId"], mocked_version["id"])
    impact_url = url + "featureImpact/"
    mock_get_response(url, mocked_version)

    responses.add(
        responses.POST,
        impact_url,
        status=200,
        content_type="application/json",
        headers={"Location": status_url},
        # this ID is ignored, we only use headers and we dont' have a real ID from the backend.
        body=json.dumps({"status_id": "5cf4d3f5f930e26daac18a1a"}),
    )

    responses.add(
        responses.GET, status_url, headers={"Location": url}, status=303,
    )

    # act
    image = CustomModelVersion.get(mocked_version["customModelId"], mocked_version["id"])
    image.calculate_feature_impact()

    # assert

    assert responses.calls[0].request.method == "GET"
    assert responses.calls[0].request.url == url
    assert responses.calls[1].request.method == "POST"
    assert responses.calls[1].request.url == impact_url
    assert responses.calls[2].request.method == "GET"
    assert responses.calls[2].request.url == status_url
