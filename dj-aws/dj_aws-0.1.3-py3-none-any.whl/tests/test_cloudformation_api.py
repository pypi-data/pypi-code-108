import json
from importlib.resources import open_text
from unittest import mock

from botocore.exceptions import ClientError
from django.test import TestCase

from djaws import s3_api, cloudformation_api
from djaws.cloudformation.exceptions import CFError


class DescribeStacksTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        with open_text('djaws.tests.schemas.cloudformation', 'describe_stacks.json') as cf_json:
            cls.r_stacks_data = json.loads(cf_json.read())

    @mock.patch.object(cloudformation_api, 'cf_session_client')
    def test_ok(self, mock_client):
        mock_client.describe_stacks.return_value = self.r_stacks_data

        r_stacks = cloudformation_api.describe_stacks(
            mock_client,
            stack_name='test123',
        )
        self.assertTrue(r_stacks.first_stack.stack_status, 'CREATE_COMPLETE')

    @mock.patch.object(cloudformation_api, 'cf_session_client')
    def test_validation_error(self, mock_client):
        mock_client.describe_stacks.side_effect = ClientError(
            {
                'Error': {
                    'Code': 'ValidationError',
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

        with self.assertRaises(CFError):
            cloudformation_api.describe_stacks(
                mock_client,
                stack_name='test123',
            )
