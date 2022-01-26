# -*- coding: utf-8 -*-

from pip_services3_commons.config import ConfigParams

from pip_services3_aws.connect.AwsConnectionParams import AwsConnectionParams


class TestAwsConnectionParams:

    def test_empty_connection(self):
        connection = AwsConnectionParams()
        assert "arn:aws::::", connection.get_arn()

    def test_parse_arn(self):
        connection = AwsConnectionParams()

        connection.set_arn("arn:aws:lambda:us-east-1:12342342332:function:pip-services-dummies")
        assert "lambda" == connection.get_service()
        assert "us-east-1" == connection.get_region()
        assert "12342342332" == connection.get_account()
        assert "function" == connection.get_resource_type()
        assert "pip-services-dummies" == connection.get_resource()

        connection.set_arn("arn:aws:s3:us-east-1:12342342332:pip-services-dummies")
        assert "s3" == connection.get_service()
        assert "us-east-1" == connection.get_region()
        assert "12342342332" == connection.get_account()
        assert connection.get_resource_type() is None
        assert "pip-services-dummies" == connection.get_resource()

        connection.set_arn("arn:aws:lambda:us-east-1:12342342332:function/pip-services-dummies")
        assert "lambda" == connection.get_service()
        assert "us-east-1" == connection.get_region()
        assert "12342342332" == connection.get_account()
        assert "function" == connection.get_resource_type()
        assert "pip-services-dummies" == connection.get_resource()

    def test_compose_ar(self):
        connection = AwsConnectionParams.from_config(
            ConfigParams.from_tuples(
                'connection.service', 'lambda',
                'connection.region', 'us-east-1',
                'connection.account', '12342342332',
                'connection.resource_type', 'function',
                'connection.resource', 'pip-services-dummies',
                'credential.access_id', '1234',
                'credential.access_key', 'ABCDEF'
            )
        )

        assert "arn:aws:lambda:us-east-1:12342342332:function:pip-services-dummies", connection.get_arn()
        assert "1234", connection.get_access_id()
        assert "ABCDEF", connection.get_access_key()
