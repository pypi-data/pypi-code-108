"""
Tests for the ObjectClerk API

Tests marked @pytest.mark.development require environment variables
to specify an s3 instance location and tokens
"""
import os
from hashlib import md5
from io import BufferedReader
from io import BytesIO
from os import environ
from pathlib import Path
from typing import Tuple
from uuid import uuid4

import boto3
import pytest

from object_clerk import ObjectClerk
from object_clerk import ObjectNotFoundException
from object_clerk import ObjectSaveException
from object_clerk.config import MULTIPART_THRESHOLD


"""
S3 endpoint configuration
"""

HOST = environ.get("OBJECT_STORE_HOST")
PORT = int(environ.get("OBJECT_STORE_PORT", 1))
ACCESS_KEY = environ.get("OBJECT_STORE_ACCESS_KEY")
SECRET_KEY = environ.get("OBJECT_STORE_SECRET_KEY")
# Configure retry to fail quickly on connection errors
RETRY = {
    "retry_delay": 1,
    "retry_backoff": 1,
    "retry_jitter": 1,
    "retry_max_delay": 1,
    "retry_tries": 1,
}


def get_abs_path(test_filename: str = None) -> str:
    """
    Return the absolute path to the test data
    :param test_filename: name of the test file in current working directory
    :return: absolute path of the test file
    """
    pwd = os.getcwd()
    return os.path.join(pwd, "object_clerk", "tests", test_filename)


"""
Fixtures for data and other dependencies
"""


@pytest.fixture(scope="session")
def boto_client() -> boto3.client:
    """
    Configure a boto3.client for s3
    :return: boto3.client instance
    """
    schema = "http"
    endpoint_url = f"{schema}://{HOST}:{PORT}/"
    return boto3.client(
        service_name="s3",
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
        endpoint_url=endpoint_url,
    )


@pytest.fixture(scope="session")
def bucket(boto_client) -> str:
    """
    Create a bucket and remove it at the end of the tests
    :param boto_client: boto3.client instance
    :return: bucket name str
    """
    # yield "inbox"
    bucket_name = "test-object-clerk"
    # Create Test Bucket
    try:
        boto_client.create_bucket(Bucket=bucket_name)
    except Exception as e:
        print(f"Exception creating: {e}")
    yield bucket_name
    # Delete Bucket
    try:
        boto_client.delete_bucket(Bucket=bucket_name)
    except Exception as e:
        print(f"Exception deleting: {e}")


@pytest.fixture(scope="session")
def empty_bucket(boto_client) -> str:
    """
    Create a bucket and remove it at the end of the tests
    :param boto_client: boto3.client instance
    :return: bucket name str
    """
    bucket_name = "empty-bucket"
    # Create Empty Bucket
    try:
        boto_client.create_bucket(Bucket=bucket_name)
    except Exception as e:
        print(f"Exception creating: {e}")
    yield bucket_name
    # Delete Empty Bucket
    try:
        boto_client.delete_bucket(Bucket=bucket_name)
    except Exception as e:
        print(f"Exception deleting: {e}")


@pytest.fixture(scope="session")
def move_bucket(boto_client) -> str:
    """
    Create a bucket and remove it at the end of the tests
    :param boto_client: boto3.client instance
    :return: bucket name str
    """
    bucket_name = "test-object-clerk-move"
    # Create Test Bucket
    try:
        boto_client.create_bucket(Bucket=bucket_name)
    except Exception as e:
        print(f"Exception creating: {e}")
    yield bucket_name
    # Delete Bucket
    try:
        boto_client.delete_bucket(Bucket=bucket_name)
    except Exception as e:
        print(f"Exception deleting: {e}")


@pytest.fixture(scope="session")
def object_store_data(boto_client, bucket) -> None:
    """
    Create objects for test cases in the bucket specified
    by the bucket param
    :param boto_client: boto3.client instance
    :param bucket: str name of the bucket to load the data in
    :return:
    """
    with open(get_abs_path("example_object"), mode="rb") as f:
        # Add Get file
        boto_client.upload_fileobj(f, Bucket=bucket, Key="get_file")
    with open(get_abs_path("example_object"), mode="rb") as f:
        # Add Delete file
        boto_client.upload_fileobj(f, Bucket=bucket, Key="delete_file")
    with open(get_abs_path("example_object"), mode="rb") as f:
        # Add Copy File
        boto_client.upload_fileobj(f, Bucket=bucket, Key="copy_file")
    with open(get_abs_path("example_object"), mode="rb") as f:
        # Add Copy File
        boto_client.upload_fileobj(f, Bucket=bucket, Key="move_file")
    yield
    # Delete objects
    boto_client.delete_object(Bucket=bucket, Key="get_file")
    boto_client.delete_object(Bucket=bucket, Key="delete_file")
    boto_client.delete_object(Bucket=bucket, Key="copy_file")
    # in case of test case failure remove the move object
    boto_client.delete_object(Bucket=bucket, Key="move_file")


@pytest.fixture(
    scope="function",
    params=[
        1,
        3,
        5,
        8,
        pytest.param(13, marks=pytest.mark.long),
        pytest.param(16, marks=pytest.mark.long),
        pytest.param(17, marks=pytest.mark.long),
        pytest.param(30, marks=pytest.mark.long),
        pytest.param(50, marks=pytest.mark.long),
    ],
)
def local_file(tmp_path_factory, request) -> Tuple[Path, int]:
    """
    Creates files locally of varying sizes based upon fixture params
    specifying a size in MB
    :param tmp_path_factory: pytest built in fixture for managing a temp directory
        3 tmp dirs are retained over test runs
    :param request: pytest built in fixture for accessing test case metadata e.g.
        fixture params
    :return: Tuple [local file path, size of file]
    """
    MB = 1024 * 1024
    size = request.param  # size in MB
    tmp_path = tmp_path_factory.mktemp(f"{uuid4().hex}_test_file_{size}_MB", numbered=False)

    file = tmp_path.joinpath(f"{size}_MB.file")
    with file.open(mode="wb") as f:
        if size == 0:
            f.write(b"")
        else:
            f.seek(size * MB - 1)
            f.write(b"\0")
    return file, size * MB


@pytest.fixture(scope="function")
def objects_of_size(local_file, bucket, object_clerk):
    """

    :param local_file:
    :param bucket:
    :param object_clerk:
    :return:
    """
    file, size = local_file
    object_key = f"object_clerk/{uuid4().hex}"
    object_clerk.upload_object(file, bucket, object_key)
    yield bucket, object_key
    # clean up
    object_clerk.delete_object(bucket, object_key)


@pytest.fixture(scope="session")
def object_clerk() -> ObjectClerk:
    """
    Fixture providing a configured instance of the Object clerk
    :return: ObjectClerk instance
    """
    return ObjectClerk(
        host=HOST,
        port=PORT,
        access_key=ACCESS_KEY,
        secret_key=SECRET_KEY,
        **RETRY,
        list_objects_page_size=1,  # force handling of multiple calls to object store
    )


"""
Test Cases
"""


@pytest.mark.development
def test_get_object_of_size(object_clerk, objects_of_size):
    """
    Given: Object clerk instance, object in the object store
    When: Getting an existing object of varying size
    Then: expected object is retrieved with valid checksum
    :param object_clerk: instance of ObjectClerk
    :param objects_of_size: fixture providing objects loaded in an object store
    :return: None
    """
    bucket, object_key = objects_of_size
    # When
    response = object_clerk.get_object(bucket, object_key, verify_checksum=True)
    # Then No errors raised
    assert True


@pytest.mark.development
def test_get_object(object_clerk, object_store_data, bucket):
    """
    Given: Object clerk instance, object in the object store
    When: Getting an existing object
    Then: expected object is retrieved
    :param object_clerk: instance of ObjectClerk
    :param object_store_data: fixture providing objects loaded in an object store
    :param bucket: name of the bucket the objects are loaded in
    :return: None
    """
    # When
    response = object_clerk.get_object(bucket, "get_file")
    # Then
    assert response == b"EXAMPLE OBJECT FOR TESTING OBJECT CLERK OPERATIONS\n"


@pytest.mark.development
@pytest.mark.parametrize(
    "bucket_name, key",
    [
        pytest.param(object, "foo", id="bad_key"),
        pytest.param("foo", "get_file", id="bad_bucket"),
        pytest.param("foo", "foo", id="bad_both"),
    ],
)
def test_get_object_not_found(object_clerk, bucket, bucket_name, key):
    """
    Given: ObjectClerk instance
    When: getting an object that is not there
    Then: receive an ObjectNotFoundException
    :param object_clerk: ObjectClerk instance
    :param bucket: Fixture providing a bucket that exists
    :param bucket_name: name of the bucket to attempt retrieval from
    :param key: name of the object to attempt retrieval of
    :return: None
    """

    # substitute bucket name with a valid bucket from the fixture
    if bucket_name is object:
        bucket_name = bucket
    # When Then
    with pytest.raises(ObjectNotFoundException):
        object_clerk.get_object(bucket_name, key)


@pytest.mark.development
def test_get_object_info(object_clerk, object_store_data, bucket):
    """
    Given: ObjectClerk instance, object in object store
    When: Getting object info for object that is present
    Then: receive expected checksum
    :param object_clerk: ObjectClerk instance
    :param object_store_data: Fixture that loaded objects into the object store
    :param bucket: Bucket containing the expected objects
    :return: None
    """
    with open(get_abs_path("example_object"), mode="rb") as f:
        checksum = md5(f.read()).hexdigest()
    # When
    response = object_clerk.get_object_info(bucket, "get_file")
    # Then
    assert response["etag"][1:-1] == checksum


@pytest.mark.development
@pytest.mark.parametrize(
    "bucket_name, key",
    [
        pytest.param(object, "foo", id="bad_key"),
        pytest.param("foo", "get_file", id="bad_bucket"),
        pytest.param("foo", "foo", id="bad_both"),
    ],
)
def test_get_object_info_not_found(object_clerk, bucket, bucket_name, key):
    """
    Given: ObjectClerk instance
    When: getting an objects info that is not there
    Then: receive an ObjectNotFoundException
    :param object_clerk: ObjectClerk instance
    :param bucket: Fixture providing a bucket that exists
    :param bucket_name: name of the bucket to attempt retrieval from
    :param key: name of the object to attempt retrieval of
    :return: None
    """
    # substitute bucket name with a valid bucket from the fixture
    if bucket_name is object:
        bucket_name = bucket
    # When Then
    with pytest.raises(ObjectNotFoundException):
        object_clerk.get_object_info(bucket_name, key)


@pytest.mark.development
def test_copy_object(object_clerk, object_store_data, bucket):
    """
    Given: ObjectClerk instance, object to copy in object store
    When: Copying object
    Then: Copy of object in the new destination
    :param object_clerk: ObjectClerk instance
    :param object_store_data: Fixture that loaded objects in the object store
    :param bucket: name of the bucket the loaded objects are in
    :return: None
    """
    source_checksum = object_clerk.get_object_info(bucket, "copy_file")["etag"][1:-1]
    # When
    object_clerk.copy_object(bucket, "copy_file", bucket, "copied_file")
    destination_checksum = object_clerk.get_object_info(bucket, "copied_file")["etag"][1:-1]
    # clean up
    object_clerk.delete_object(bucket, "copied_file")
    # Then
    assert source_checksum == destination_checksum


@pytest.mark.development
def test_delete_object(object_clerk, object_store_data, bucket):
    """
    Given: ObjectClerk instance, object in the object store
    When: Deleting the existing object
    Then: Object is not found when attempting retrieval
    :param object_clerk: ObjectClerk instance
    :param object_store_data: Fixture that loaded data in the object store
    :param bucket: Name of the bucket the object is loaded in
    :return: None
    """
    response = object_clerk.get_object_info(bucket, "delete_file")
    assert isinstance(response, dict)
    # When
    object_clerk.delete_object(bucket, "delete_file")
    # Then
    with pytest.raises(ObjectNotFoundException):
        _ = object_clerk.get_object_info(bucket, "delete_file")


# str, Path, BufferedReader, BytesIO, bytes
@pytest.mark.development
@pytest.mark.parametrize(
    "file",
    [
        pytest.param(get_abs_path("example_object"), id="str"),
        pytest.param(Path(get_abs_path("example_object")), id="Path"),
        pytest.param(
            BufferedReader(BytesIO(b"EXAMPLE OBJECT FOR TESTING OBJECT CLERK OPERATIONS\n")),
            id="BufferedReader",
        ),
        pytest.param(
            BytesIO(b"EXAMPLE OBJECT FOR TESTING OBJECT CLERK OPERATIONS\n"), id="BytesIO"
        ),
        pytest.param(b"EXAMPLE OBJECT FOR TESTING OBJECT CLERK OPERATIONS\n", id="bytes"),
    ],
)
def test_upload_object(object_clerk, bucket, file):
    """
    Given: ObjectClerk instance, file to upload
    When: upload object to object store
    Then: Object can be retrieved from the object store
    :param object_clerk: ObjectClerk instance
    :param bucket: Name of the bucket to upload to
    :param file: File to upload
    :return: None
    """
    with open(get_abs_path("example_object"), mode="rb") as f:
        checksum = md5(f.read()).hexdigest()
    # When
    object_clerk.upload_object(file, bucket, "upload_file")
    etag = object_clerk.get_object_info(bucket, "upload_file")["etag"]
    # clean up
    object_clerk.delete_object(bucket, "upload_file")
    # Then
    assert etag[1:-1] == checksum


@pytest.mark.development
def test_upload_object_checksums_by_size(object_clerk, local_file, bucket):
    """
    Given: ObjectClerk instance, object to upload and its size
    :param object_clerk: ObjectClerk instance
    :param local_file: Fixture providing a file and its size
    :param bucket: Bucket to load the object into
    :return: None
    """

    def calculate_s3_etag():
        """
        Alternate checksum calculation implementation to validate object clerk
        checksum calculation
        :return: expected s3 etag
        """
        md5s = []
        with file_path.open("rb") as fp:
            while True:
                data = fp.read(MULTIPART_THRESHOLD)
                if not data:
                    break
                md5s.append(md5(data))
        if len(md5s) == 1 and size != MULTIPART_THRESHOLD:
            return '"{}"'.format(md5s[0].hexdigest())
        digests = b"".join(m.digest() for m in md5s)
        digests_md5 = md5(digests)
        return '"{}-{}"'.format(digests_md5.hexdigest(), len(md5s))

    file_path, size = local_file
    object_key = f"object_clerk/test/{uuid4().hex}.file"
    checksum = calculate_s3_etag()
    # When
    object_clerk.upload_object(file_path, bucket, object_key)

    etag = object_clerk.get_object_info(bucket, object_key)["etag"]
    # clean up
    object_clerk.delete_object(bucket, object_key)
    # Then
    assert etag == checksum


@pytest.mark.development
def test_upload_object_metadata(object_clerk, local_file, bucket):
    """
    Given: ObjectClerk instance, object to upload
    When: Uploading the object with extra header parameters
    Then: The headers can be read and parsed
    :param object_clerk: ObjectClerk instance
    :param local_file: Fixture providing a file and its size
    :param bucket: Bucket to load the object into
    :return: None
    """
    file_path, _ = local_file
    object_key = f"object_clerk/test/{uuid4().hex}.file"
    # When
    dataset_id = uuid4().hex
    metadata = {"groupname": "DATASET", "groupid": dataset_id, "objecttype": "FILE"}
    object_clerk.upload_object(file_path, bucket, object_key, metadata=metadata)
    file_headers = object_clerk.get_object_info(bucket=bucket, object_key=object_key)
    assert file_headers["x-amz-meta-groupid"] == dataset_id
    assert file_headers["x-amz-meta-groupname"] == "DATASET"
    assert file_headers["x-amz-meta-objecttype"] == "FILE"
    # clean up
    object_clerk.delete_object(bucket, object_key)


@pytest.mark.development
def test_upload_empty_file(object_clerk, bucket):
    """
    Given: Object clerk instance
    When: Uploading an empty file
    Then: Receive a ObjectSaveException
    :param object_clerk: ObjectClerk instance
    :param bucket: Name of the bucket to upload to
    :return: None
    """
    # When Then
    with pytest.raises(ObjectSaveException):
        object_clerk.upload_object(b"", bucket, "object_clerk/test/empty")


@pytest.mark.development
def test_move_object(object_clerk, bucket, object_store_data, move_bucket):
    """
    Given: ObjectClerk instance, object that exists
    When: Move existing object to new bucket, object key
    Then: Object is available in new location and not available in the old one
    :param object_clerk: ObjectClerk instance
    :param bucket: Bucket the existing object is in
    :param object_store_data: Fixture that loaded objects
    :param move_bucket: Bucket to move to
    :return: None
    """
    source_checksum = object_clerk.get_object_info(bucket, "copy_file")["etag"][1:-1]
    # When
    object_clerk.move_object(bucket, "move_file", move_bucket, "moved_file")
    destination_checksum = object_clerk.get_object_info(move_bucket, "moved_file")["etag"][1:-1]
    # clean up
    object_clerk.delete_object(move_bucket, "moved_file")
    # Then
    assert source_checksum == destination_checksum
    with pytest.raises(ObjectNotFoundException):
        object_clerk.get_object_info(bucket, "move_file")


@pytest.mark.development
def test_list_objects_not_truncated(object_clerk, bucket, object_store_data):
    """
    Given: ObjectClerk instance, objects that exist in bucket
    When: Querying what objects exist in a bucket
    Then: List of bucket contents is obtained
    :param object_clerk: ObjectClerk instance
    :param bucket: Bucket the existing object is in
    :param object_store_data: Fixture that loaded objects
    :return: None
    """
    contents = object_clerk.list_objects(bucket)
    # because object_clerk is session scoped, can be from 2 to 4 objects,
    # depending on the order that tests are run
    object_ids = [content["Key"] for content in contents]
    assert len(object_ids) >= 2
    assert "copy_file" in object_ids
    assert "get_file" in object_ids


@pytest.mark.development
def test_list_objects_invalid_bucket(object_clerk, bucket, object_store_data):
    with pytest.raises(ObjectNotFoundException):
        next(object_clerk.list_objects("false_bucket"))


@pytest.mark.development
def test_list_objects_empty_bucket(object_clerk, empty_bucket):
    contents = object_clerk.list_objects(empty_bucket)
    with pytest.raises(StopIteration):
        next(contents)


@pytest.mark.development
def test_list_objects_prefix(object_clerk, bucket, object_store_data):
    """
    Given: ObjectClerk instance, multiple objects that exist in bucket
    When: Querying what objects exist with a prefix in a bucket
    Then: List of bucket contents is obtained
    :param object_clerk: ObjectClerk instance
    :param bucket: Bucket the existing object is in
    :param object_store_data: Fixture that loaded objects
    :return: None
    """
    contents = object_clerk.list_objects(bucket, prefix="cop")
    contents = list(contents)
    assert len(contents) == 1
    assert contents[0]["Key"] == "copy_file"


def test_pass():
    # work around for pipeline without any non development marked tests
    assert True
