import os
import tempfile
import unittest
import unittest.mock
import uuid
from pathlib import Path

import boto3
from botocore.exceptions import NoCredentialsError

from erezutils import (
    chunks,
    delete_from_s3,
    list_s3_bucket_keys,
    pgpass,
    pgpass_escape,
    rupdate,
)

BUCKET = "erezutils-test-bucket"


class RecursiveUpdateTest(unittest.TestCase):
    def test_update_empty(self):
        self.assertEqual({"a": 1}, rupdate({}, {"a": 1}))

    def test_update_existing(self):
        self.assertEqual({"a": 2}, rupdate({"a": 1}, {"a": 2}))

    def test_update_with_other_keys(self):
        self.assertEqual({"a": 2, "b": 1}, rupdate({"a": 1}, {"a": 2, "b": 1}))

    def test_update_leaves_other_keys_untouched(self):
        self.assertEqual({"a": 2, "b": 1}, rupdate({"a": 1, "b": 1}, {"a": 2}))

    def test_recursive_update(self):
        self.assertEqual({"a": {"b": 2}}, rupdate({"a": {"b": 1}}, {"a": {"b": 2}}))

    def test_recursive_update_on_empty_dict(self):
        self.assertEqual({"a": {"b": 2}}, rupdate({}, {"a": {"b": 2}}))

    def test_recursive_update_with_other_keys(self):
        self.assertEqual(
            {"a": {"b": 2, "c": 1}}, rupdate({"a": {"b": 1}}, {"a": {"b": 2, "c": 1}})
        )

    def test_recursive_update_leaves_other_keys_untouched(self):
        self.assertEqual(
            {"a": {"b": 2, "c": 1}}, rupdate({"a": {"b": 1, "c": 1}}, {"a": {"b": 2}})
        )


class ChunksTest(unittest.TestCase):
    def test_empty(self):
        data = []
        self.assertEqual([], list(chunks(data, 1)))

    def test_one_chunk(self):
        data = [1]
        self.assertEqual([[1]], list(chunks(data, 1)))

    def test_chuck_group_1(self):
        data = [1, 2]
        self.assertEqual([[1], [2]], list(chunks(data, 1)))

    def test_chunk_group_2(self):
        data = [1, 2, 3, 4]
        self.assertEqual([[1, 2], [3, 4]], list(chunks(data, 2)))


def test_bucket_access():
    s3 = boto3.resource("s3")
    bucket = s3.Bucket(BUCKET)
    try:
        # Contact S3.
        bucket.creation_date
    except NoCredentialsError:
        return True
    return False


@unittest.skipIf(test_bucket_access(), "Cannot access AWS bucket")
class S3OperationsTest(unittest.TestCase):
    # Prevent conflicts between concurrent test runs.
    PREFIX = str(uuid.uuid4())

    def setUp(self):
        super().setUp()
        self.s3_client = boto3.client("s3")

    def tearDown(self):
        remaining_keys = self.list_keys()
        delete_from_s3(self.s3_client, BUCKET, remaining_keys)
        super().tearDown()

    def make_key(self, filename):
        return self.PREFIX + filename

    def create_file(self, filename):
        key = self.make_key(filename)
        self.s3_client.put_object(Bucket=BUCKET, Key=key)

    def list_keys(self):
        return list_s3_bucket_keys(self.s3_client, BUCKET, Prefix=self.PREFIX)

    def test_list_file(self):
        filename = "a_file"
        self.create_file(filename)
        self.assertEqual([self.make_key(filename)], self.list_keys())

    def test_list_nested_files(self):
        file1 = "dir1/f1"
        file2 = "dir2/f1"
        self.create_file(file1)
        self.create_file(file2)
        self.assertEqual([self.make_key(file1), self.make_key(file2)], self.list_keys())

    def test_clean_files(self):
        filename = "a_file"
        self.create_file(filename)
        delete_from_s3(self.s3_client, BUCKET, [self.make_key(filename)])
        self.assertEqual([], self.list_keys())


class PGPassEscapeTest(unittest.TestCase):
    def test_escape(self):
        cases = [
            ("abc123", "abc123"),
            ("abc:123", "abc\\:123"),
            ("abc*123", "abc\\*123"),
            ("abc\\123", "abc\\\\123"),
            ("abc:*\\123", "abc\\:\\*\\\\123"),
        ]
        for value, expected in cases:
            with self.subTest(value):
                self.assertEqual(expected, pgpass_escape(value))


class PGPassTest(unittest.TestCase):
    def test_context_manager(self):
        configs = [
            {
                "name": "db1",
                "user": "admin1",
                "password": "hunter2",
                "host": "localhost",
            },
            {
                "name": "db2",
                "user": "admin2",
                "password": "hunter:2",
                "host": "localhost",
            },
        ]
        with pgpass(configs) as path:
            content = Path(path).read_bytes()
            self.assertEqual(
                b"localhost:*:db1:admin1:hunter2\n"
                b"localhost:*:db2:admin2:hunter\\:2\n",
                content,
            )
        self.assertFalse(os.path.exists(path))

    def test_merges_with_user_pgpass(self):
        with tempfile.TemporaryDirectory() as testdir_cm:
            testdir = Path(testdir_cm)
            with unittest.mock.patch("pathlib.Path.home", return_value=testdir):
                home_pgpass_path = testdir / ".pgpass"
                with open(home_pgpass_path, "w") as home_pgpass:
                    home_pgpass.write("somehost:*:dbname:username:Passw0rd!\n")
                config = [
                    {
                        "name": "db1",
                        "user": "admin1",
                        "password": "hunter2",
                        "host": "localhost",
                    }
                ]
                with pgpass(config) as path:
                    content = Path(path).read_bytes()
                    self.assertEqual(
                        b"somehost:*:dbname:username:Passw0rd!\n"
                        b"localhost:*:db1:admin1:hunter2\n",
                        content,
                    )
                self.assertFalse(os.path.exists(path))
                self.assertTrue(home_pgpass_path.exists())

    def test_merges_with_user_pgpass_without_line_return(self):
        with tempfile.TemporaryDirectory() as testdir_cm:
            testdir = Path(testdir_cm)
            with unittest.mock.patch("pathlib.Path.home", return_value=testdir):
                home_pgpass_path = testdir / ".pgpass"
                with open(home_pgpass_path, "w") as home_pgpass:
                    home_pgpass.write("somehost:*:dbname:username:Passw0rd!")
                config = [
                    {
                        "name": "db1",
                        "user": "admin1",
                        "password": "hunter2",
                        "host": "localhost",
                    }
                ]
                with pgpass(config) as path:
                    content = Path(path).read_bytes()
                    self.assertEqual(
                        b"somehost:*:dbname:username:Passw0rd!\n"
                        b"localhost:*:db1:admin1:hunter2\n",
                        content,
                    )
                self.assertFalse(os.path.exists(path))
                self.assertTrue(home_pgpass_path.exists())
