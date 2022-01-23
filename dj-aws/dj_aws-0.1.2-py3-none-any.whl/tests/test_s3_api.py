import json
from importlib.resources import open_text
from unittest import mock

from botocore.exceptions import ClientError
from django.test import TestCase

from djaws import s3_api
from djaws.s3.exceptions import S3Error, BucketAlreadyExists, BucketAlreadyOwnedByYouError


class CreatePublicAccessBucketTests(TestCase):
    @mock.patch.object(s3_api, 'create_bucket')
    @mock.patch.object(s3_api, 'put_public_access_block')
    @mock.patch.object(s3_api, 'put_bucket_cors')
    def test_ok(self, mock_create_bucket, mock_put_public_access_block, mock_put_bucket_cors):
        mock_create_bucket.return_value = None
        mock_put_public_access_block.return_value = True
        mock_put_bucket_cors.return_value = True

        r_bucket = s3_api.create_public_access_bucket(
            s3_api.s3_session_client(),
            bucket='my-test-bucket-2',
        )
        self.assertTrue(r_bucket)


class CreateBucketTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        with open_text('djaws.tests.schemas.s3', 'create_bucket.json') as bucket_json:
            cls.r_bucket_data = json.loads(bucket_json.read())

    @mock.patch.object(s3_api, 's3_session_client')
    def test_ok(self, mock_client):
        mock_client.create_bucket.return_value = self.r_bucket_data

        r_bucket = s3_api.create_bucket(
            mock_client,
            bucket='bucket1',
            region='us-west-1',
        )
        self.assertEquals(
            r_bucket.location,
            'http://examplebucket.s3.amazonaws.com/'
        )

    @mock.patch.object(s3_api, 's3_session_client')
    def test_ok_no_region(self, mock_client):
        mock_client.create_bucket.return_value = self.r_bucket_data

        r_bucket = s3_api.create_bucket(
            mock_client,
            bucket='bucket1',
        )
        self.assertEquals(
            r_bucket.location,
            'http://examplebucket.s3.amazonaws.com/'
        )

    @mock.patch.object(s3_api, 's3_session_client')
    def test_BucketAlreadyExists(self, mock_client):
        mock_client.create_bucket.side_effect = ClientError(
            {
                'Error': {
                    'Code': 'BucketAlreadyExists',
                    'Message': 'Details/context around the exception or error'
                },
                'ResponseMetadata': {
                    'RequestId': '1234567890ABCDEF',
                    'HostId': 'host ID data will appear here as a hash',
                    'HTTPStatusCode': 400,
                    'HTTPHeaders': {'header metadata key/values will appear here'},
                    'RetryAttempts': 0
                }
            },
            'generate_presigned_post'
        )

        with self.assertRaises(BucketAlreadyExists):
            s3_api.create_bucket(
                mock_client,
                bucket='bucket1',
            )


class PutPublicAccessBlockTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.access_block_data = {
            'bucket': 'bucket1',
            'config': s3_api.PublicAccessBlockConfiguration(
                block_public_acls=False,
                ignore_public_acls=False,
                block_public_policy=False,
                restrict_public_buckets=False,
            )
        }

    @mock.patch.object(s3_api, 's3_session_client')
    def test_put_public_access_block_ok(self, mock_client):
        mock_client.put_public_access_block.return_value = True

        r_access_block = s3_api.put_public_access_block(
            mock_client,
            **self.access_block_data,
        )
        self.assertTrue(r_access_block)

    @mock.patch.object(s3_api, 's3_session_client')
    def test_put_public_access_block_error(self, mock_client):
        mock_client.put_public_access_block.side_effect = ClientError(
            error_response=dict(),
            operation_name='put_public_access_block'
        )

        with self.assertRaises(S3Error):
            s3_api.put_public_access_block(
                mock_client,
                **self.access_block_data,
            )


class CreateBucketCORSTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.cors_data = {
            'bucket': 'bucket1',
            'cors_config': {
                'CORSRules': [
                    {
                        "AllowedHeaders": [
                            "*"
                        ],
                        "AllowedMethods": [
                            "GET"
                        ],
                        "AllowedOrigins": [
                            "*"
                        ],
                        "MaxAgeSeconds": 3000
                    },
                ],
            },
        }

    @mock.patch.object(s3_api, 's3_session_client')
    def test_put_bucket_cors_ok(self, mock_client):
        mock_client.put_bucket_cors.return_value = True

        r_cors = s3_api.put_bucket_cors(
            mock_client,
            **self.cors_data,
        )
        self.assertTrue(r_cors)

    @mock.patch.object(s3_api, 's3_session_client')
    def test_put_bucket_cors_error(self, mock_client):
        mock_client.put_bucket_cors.side_effect = ClientError(
            error_response=dict(),
            operation_name='put_bucket_cors'
        )

        with self.assertRaises(S3Error):
            s3_api.put_bucket_cors(
                mock_client,
                **self.cors_data,
            )


class UploadObjectTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.upload_data = {
            'data': b'test_image',
            'bucket': 'bucket1',
            'uri': 'https://example.com/test.jpg',
            'key': '998adad2-c217-402e-b259-ace44a26dff4.jpg'
        }

    @mock.patch.object(s3_api, 's3_session_client')
    def test_ok(self, mock_client):
        mock_client.put_object.return_value = None

        r_upload = s3_api.upload_object(
            mock_client,
            **self.upload_data,
        )
        self.assertEquals(
            r_upload.public_s3_url,
            'https://bucket1.s3.amazonaws.com/998adad2-c217-402e-b259-ace44a26dff4.jpg'
        )

    @mock.patch.object(s3_api, 's3_session_client')
    def test_ok_no_object_name(self, mock_client):
        mock_client.put_object.return_value = None

        upload_data = self.upload_data
        upload_data.pop('key')

        r_upload = s3_api.upload_object(
            mock_client,
            **upload_data,
        )
        self.assertTrue(r_upload.public_s3_url.startswith('https://bucket1.s3.amazonaws.com/'))
        self.assertTrue(r_upload.public_s3_url.endswith('.jpg'))

    @mock.patch.object(s3_api, 's3_session_client')
    def test_client_error(self, mock_client):
        mock_client.put_object.side_effect = ClientError(
            error_response=dict(),
            operation_name='put_object'
        )

        with self.assertRaises(S3Error):
            s3_api.upload_object(
                mock_client,
                **self.upload_data,
            )


class GeneratePresignedPostTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.generate_presigned_post = {
            'bucket': 'bucket1',
            'object_name': '998adad2-c217-402e-b259-ace44a26dff4.jpg'
        }
        with open_text('djaws.tests.schemas.s3', 'generate_presigned_post.json') as generate_presigned_post_json:
            cls.r_generate_presigned_post_data = json.loads(generate_presigned_post_json.read())

    @mock.patch.object(s3_api, 's3_session_client')
    def test_generate_presigned_post_ok(self, mock_client):
        mock_client.generate_presigned_post.return_value = self.r_generate_presigned_post_data

        r_generate_presigned_post = s3_api.generate_presigned_post(
            mock_client,
            **self.generate_presigned_post,
        )
        self.assertEquals(r_generate_presigned_post.url, 'https://mybucket.s3.amazonaws.com')
        self.assertEquals(r_generate_presigned_post.fields['acl'], 'public-read')
        self.assertEquals(r_generate_presigned_post.fields['key'], 'mykey')
        self.assertEquals(r_generate_presigned_post.fields['signature'], 'mysignature')
        self.assertEquals(r_generate_presigned_post.fields['policy'], 'mybase64 encoded policy')

    @mock.patch.object(s3_api, 's3_session_client')
    def test_upload_object_error(self, mock_client):
        mock_client.generate_presigned_post.side_effect = ClientError(
            {
                'Error': {
                    'Code': 'NotAuthorizedException',
                    'Message': 'Details/context around the exception or error'
                },
                'ResponseMetadata': {
                    'RequestId': '1234567890ABCDEF',
                    'HostId': 'host ID data will appear here as a hash',
                    'HTTPStatusCode': 400,
                    'HTTPHeaders': {'header metadata key/values will appear here'},
                    'RetryAttempts': 0
                }
            },
            'generate_presigned_post'
        )

        with self.assertRaises(S3Error):
            s3_api.generate_presigned_post(
                mock_client,
                **self.generate_presigned_post,
            )
