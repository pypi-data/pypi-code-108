from unittest.mock import call, patch, MagicMock
from urllib.parse import urlparse
import json

from minio.error import S3Error
import pytest

from server.minioclient import MinioClient, MinIOPolicyStatement, generate_policy
import server.config as config


def test_generate_policy():
    statement1 = MinIOPolicyStatement()
    statement2 = MinIOPolicyStatement(buckets=['bucket1', 'bucket2'],
                                      actions=["action1", "action2"],
                                      source_ips=["ip1", "ip2"])
    statement3 = MinIOPolicyStatement(buckets=['bucket2'],
                                      actions=["action1", "action3"],
                                      allow=False, not_source_ips=["ip3"])

    assert generate_policy([statement1, statement2, statement3]) == {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Action": ["s3:*"],
                "Effect": "Allow",
                "Resource": ['arn:aws:s3:::*', 'arn:aws:s3:::*/*'],
            },
            {
                "Action": ["action1", "action2"],
                "Effect": "Allow",
                "Resource": ['arn:aws:s3:::bucket1', 'arn:aws:s3:::bucket2',
                             'arn:aws:s3:::bucket1/*', 'arn:aws:s3:::bucket2/*'],
                "Condition": {
                    "IpAddress": {
                        "aws:SourceIp": ["ip1", "ip2"]
                    }
                }
            },
            {
                "Action": ["action1", "action3"],
                "Effect": "Deny",
                "Resource": ['arn:aws:s3:::bucket2', 'arn:aws:s3:::bucket2/*'],
                "Condition": {
                    "NotIpAddress": {
                        "aws:SourceIp": ["ip3"]
                    }
                }
            }
        ]
    }


@patch("server.minioclient.Minio", autospec=True)
@patch("subprocess.check_call")
def test_client_instantiation__defaults(subproc_mock, minio_mock):
    MinioClient()
    minio_mock.assert_called_once_with(endpoint=urlparse(config.MINIO_URL).netloc,
                                       access_key=config.MINIO_ROOT_USER, secret_key=config.MINIO_ROOT_PASSWORD,
                                       secure=False)
    subproc_mock.assert_called_once_with(['mcli', '-q', '--no-color', 'alias', 'set',
                                          config.MINIO_ADMIN_ALIAS, config.MINIO_URL,
                                          config.MINIO_ROOT_USER, config.MINIO_ROOT_PASSWORD])


@patch("server.minioclient.Minio", autospec=True)
@patch("subprocess.check_call")
def test_client_instantiation__custom_params(subproc_mock, minio_mock):
    MinioClient(url="http://hello-world", user="accesskey", secret_key="secret_key", alias="toto")
    minio_mock.assert_called_once_with(endpoint="hello-world", access_key="accesskey",
                                       secret_key="secret_key", secure=False)
    subproc_mock.assert_called_once_with(['mcli', '-q', '--no-color', 'alias', 'set',
                                          "toto", "http://hello-world", "accesskey", "secret_key"])


@patch("server.minioclient.Minio", autospec=True)
@patch("subprocess.check_call")
def test_client_instantiation__no_aliases(subproc_mock, minio_mock):
    MinioClient(url="http://hello-world", user="accesskey", secret_key="secret_key", alias=None)
    minio_mock.assert_called_once_with(endpoint="hello-world", access_key="accesskey",
                                       secret_key="secret_key", secure=False)
    subproc_mock.assert_not_called()


@patch("server.minioclient.Minio", autospec=True)
@patch("subprocess.check_call")
def test_client_remove_alias(subproc_mock, minio_mock):
    client = MinioClient(url="http://hello-world", user="accesskey", secret_key="secret_key", alias="toto")
    subproc_mock.assert_called_once_with(['mcli', '-q', '--no-color', 'alias', 'set',
                                          "toto", "http://hello-world", "accesskey", "secret_key"])

    client.remove_alias()
    subproc_mock.assert_called_with(['mcli', '-q', '--no-color', 'alias', 'rm', "toto"])


@patch("subprocess.check_call")
def test_is_local_url(subproc_mock):
    minio = MinioClient(url="http://10.42.0.1:9000")

    assert minio.is_local_url("http://10.42.0.1:9000/toto")
    assert not minio.is_local_url("http://hello-world/toto")

    minio = MinioClient(url="http://hello-world")
    assert not minio.is_local_url("http://10.42.0.1:9000/toto")
    assert minio.is_local_url("http://hello-world/toto")


class MockStream:
    def iter_content(self, _):
        yield b'hello world'

    def raise_for_status(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass


@patch("server.minioclient.requests.get", return_value=MockStream())
@patch("server.minioclient.Minio", autospec=True)
@patch("server.minioclient.tempfile.NamedTemporaryFile", autospec=True)
@patch("subprocess.check_call")
def test_save_boot_artifact(subproc_mock, named_temp_mock, minio_mock, get_mock):
    client = MinioClient()

    named_temp_mock().__enter__().name = "/tmp/temp_file"
    client.save_boot_artifact("https://toto.com/path", "/toto/path")

    client._client.fput_object.assert_called_once_with("boot", "/toto/path", "/tmp/temp_file")


@patch("server.minioclient.Minio", autospec=True)
@patch("server.minioclient.TarFile.open", autospec=True)
@patch("subprocess.check_call")
def test_extract_archive(subproc_mock, tarfile_mock, minio_mock):
    client = MinioClient()

    archive_mock = tarfile_mock.return_value.__enter__.return_value
    file_obj = MagicMock()
    members = [MagicMock(isfile=MagicMock(return_value=True), size=42),
               MagicMock(isfile=MagicMock(return_value=False)),
               None]
    members[0].name = "toto"
    archive_mock.next = MagicMock(side_effect=members)

    client.extract_archive(file_obj, "bucket/rootpath")

    tarfile_mock.assert_called_once_with(fileobj=file_obj, mode='r')
    archive_mock.extractfile.assert_called_once_with(members[0])

    client._client.put_object.assert_called_once_with("bucket/rootpath",
                                                      "toto",
                                                      archive_mock.extractfile(),
                                                      members[0].size,
                                                      num_parallel_uploads=1)


@patch("server.minioclient.Minio", autospec=True)
@patch("subprocess.check_call")
def test_make_bucket(subproc_mock, minio_mock):
    client = MinioClient()
    client._client = MagicMock()
    client.make_bucket('test-id')
    client._client.make_bucket.assert_called_once_with('test-id')

    def side_effect(*arg, **kwargs):
        raise S3Error('code', 'message', 'resource', 'request_id', 'host_id', 'response')
    client._client.make_bucket.side_effect = side_effect

    with pytest.raises(ValueError) as exc:
        client.make_bucket('test-id')
    assert "The bucket already exists" in str(exc.value)


@patch("server.minioclient.Minio", autospec=True)
@patch("subprocess.check_call")
def test_remove_bucket(subproc_mock, minio_mock):
    client = MinioClient(url='http://test.invalid', user='test', secret_key='test', alias="local")
    client.remove_bucket('test-id')
    subproc_mock.assert_has_calls([
        call(['mcli', '-q', '--no-color', 'alias', 'set', 'local', 'http://test.invalid', 'test', 'test']),
        call(['mcli', '-q', '--no-color', 'rb', '--force', 'local/test-id'])])


@patch("server.minioclient.Minio", autospec=True)
@patch("subprocess.check_call")
def test_minio_add_user(subproc_mock, minio_mock):
    client = MinioClient(url='http://test.invalid', user='test', secret_key='test', alias="local")
    client.add_user('job-id-c', 'job-password')
    subproc_mock.assert_has_calls([
        call(['mcli', '-q', '--no-color', 'alias', 'set', 'local', 'http://test.invalid', 'test', 'test']),
        call(['mcli', '-q', '--no-color', 'admin', 'user', 'add', 'local', 'job-id-c', 'job-password']),
    ])


@patch("server.minioclient.Minio", autospec=True)
@patch("subprocess.check_call")
def test_minio_remove_user(subproc_mock, minio_mock):
    client = MinioClient(url='http://test.invalid', user='test', secret_key='test', alias="local")
    client.remove_user('username')
    subproc_mock.assert_has_calls([
        call(['mcli', '-q', '--no-color', 'alias', 'set', 'local', 'http://test.invalid', 'test', 'test']),
        call(['mcli', '-q', '--no-color', 'admin', 'user', 'remove', 'local', 'username']),
    ])


@patch("server.minioclient.Minio", autospec=True)
@patch("subprocess.check_call")
@patch("subprocess.check_output", return_value="""{"status": "success", "accessKey": "username",
    "userStatus": "enabled", "memberOf": ["group1", "group2"]}""")
def test_minio_groups_user_is_in(subproc_mock, _, minio_mock):
    client = MinioClient(url='http://test.invalid', user='test', secret_key='test', alias="local")
    assert client.groups_user_is_in() == ["group1", "group2"]
    assert client.groups_user_is_in('username') == ["group1", "group2"]
    subproc_mock.assert_has_calls([
        call(['mcli', '-q', '--no-color', '--json', 'admin', 'user', 'info', 'local', 'test']),
        call(['mcli', '-q', '--no-color', '--json', 'admin', 'user', 'info', 'local', 'username'])
    ])


@patch("server.minioclient.Minio", autospec=True)
@patch("subprocess.check_call")
def test_minio_add_user_to_group(subproc_mock, minio_mock):
    client = MinioClient(url='http://test.invalid', user='test', secret_key='test', alias="local")
    client.add_user_to_group('username', 'groupname')
    subproc_mock.assert_has_calls([
        call(['mcli', '-q', '--no-color', 'alias', 'set', 'local', 'http://test.invalid', 'test', 'test']),
        call(['mcli', '-q', '--no-color', 'admin', 'group', 'add', 'local', 'groupname', 'username']),
    ])


@patch("subprocess.check_call")
@patch("server.minioclient.tempfile.NamedTemporaryFile", autospec=True)
def test_minio_add_user_policy_add(named_temp_mock, subproc_mock):
    temp_mock = MagicMock()
    temp_mock.name = '/tmp/temp_file'
    named_temp_mock.return_value.__enter__.return_value = temp_mock

    policy_statements = [MinIOPolicyStatement(['bucket'])]
    expected_policy = generate_policy(policy_statements)

    client = MinioClient(url='http://test.invalid', user='test', secret_key='test', alias="local")
    client.apply_user_policy('policy_name', 'username', policy_statements=policy_statements)

    temp_mock.write.assert_called_once_with(json.dumps(expected_policy).encode())

    subproc_mock.assert_has_calls([
        call(['mcli', '-q', '--no-color', 'alias', 'set', 'local', 'http://test.invalid', 'test', 'test']),
        call(['mcli', '-q', '--no-color', 'admin', 'policy', 'add', 'local', 'policy_name', '/tmp/temp_file']),
        call(['mcli', '-q', '--no-color', 'admin', 'policy', 'set', 'local', 'policy_name', 'user=username'])])


@patch("subprocess.check_call")
def test_minio_remove_user_policy(subproc_mock):
    client = MinioClient(url='http://test.invalid', user='test', secret_key='test', alias="local")
    client.remove_user_policy('policy_name', 'username')

    subproc_mock.assert_has_calls([
        call(['mcli', '-q', '--no-color', 'alias', 'set', 'local', 'http://test.invalid', 'test', 'test']),
        call(['mcli', '-q', '--no-color', 'admin', 'policy', 'unset', 'local', 'policy_name', 'user=username']),
        call(['mcli', '-q', '--no-color', 'admin', 'policy', 'remove', 'local', 'policy_name'])])


def test_create_valid_bucket_name():
    # Name is too short
    assert MinioClient.create_valid_bucket_name("") == "b--x"
    assert MinioClient.create_valid_bucket_name("ab") == "b--ab"

    # Name is too long
    bucket_name = "rhjfklsahjfkdlsahuifeohwuiafohuiofhueioahufieohauiefohuaieofhuiffdsarewfgdsa"
    assert len(MinioClient.create_valid_bucket_name(bucket_name)) == 63

    # Wrong characters
    assert MinioClient.create_valid_bucket_name("/*_~!@#$%^&*()_+|") == "x-----------------x"

    # IP address
    assert MinioClient.create_valid_bucket_name("192.168.5.4") == "ip-192.168.5.4"
