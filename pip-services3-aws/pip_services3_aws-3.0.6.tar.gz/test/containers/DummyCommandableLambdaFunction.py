# -*- coding: utf-8 -*-
from pip_services3_commons.refer import Descriptor

from pip_services3_aws.containers.CommandableLambdaFunction import CommandableLambdaFunction
from test.DummyFactory import DummyFactory


class DummyCommandableLambdaFunction(CommandableLambdaFunction):
    def __init__(self):
        super().__init__("dummy", "Dummy lambda function")
        self._dependency_resolver.put('controller',
                                      Descriptor('pip-services-dummies', 'controller', 'default', '*', '*'))
        self._factories.add(DummyFactory())
