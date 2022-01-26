# -*- coding: utf-8 -*-
from pip_services3_commons.config import ConfigParams

from test.Dummy import Dummy
from test.services.DummyLambdaFunction import DummyLambdaFunction

DUMMY1: Dummy = Dummy(None, 'Key 1', 'Content 1')
DUMMY2: Dummy = Dummy(None, 'Key 2', 'Content 2')


class TestDummyCommandableLambdaService:
    lambda_func: DummyLambdaFunction = None

    @classmethod
    def setup_class(cls):
        config = ConfigParams.from_tuples(
            'logger.descriptor', 'pip-services:logger:console:default:1.0',
            'controller.descriptor', 'pip-services-dummies:controller:default:default:1.0',
            'service.descriptor', 'pip-services-dummies:service:commandable-lambda:default:1.0'
        )

        cls.lambda_func = DummyLambdaFunction()
        cls.lambda_func.configure(config)
        cls.lambda_func.open(None)

    @classmethod
    def teardown_class(cls):
        cls.lambda_func.close(None)

    def tests_crud_operations(self):
        # Create one dummy
        dummy1 = self.lambda_func.act({
            'cmd': 'dummies.create_dummy',
            'dummy': DUMMY1
        })

        assert dummy1.content == DUMMY1.content
        assert dummy1.key == DUMMY1.key

        # Create another dummy
        dummy2 = self.lambda_func.act({
            'cmd': 'dummies.create_dummy',
            'dummy': DUMMY2
        })

        assert dummy2.content == DUMMY2.content
        assert dummy2.key == DUMMY2.key

        # Update the dummy
        dummy1.content = 'Updated Content 1'
        updated_dummy1 = self.lambda_func.act({
            'cmd': 'dummies.update_dummy',
            'dummy': dummy1
        })

        assert updated_dummy1.id == dummy1.id
        assert updated_dummy1.content == dummy1.content
        assert updated_dummy1.key == dummy1.key
        dummy1 = updated_dummy1

        # Delete dummy
        self.lambda_func.act({
            'cmd': 'dummies.delete_dummy',
            'dummy_id': dummy1.id
        })

        dummy = self.lambda_func.act({
            'cmd': 'dummies.get_dummy_by_id',
            'dummy_id': dummy1.id
        })

        assert (dummy or None) is None
