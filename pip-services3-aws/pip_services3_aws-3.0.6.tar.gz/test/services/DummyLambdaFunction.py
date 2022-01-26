# -*- coding: utf-8 -*-
from pip_services3_aws.containers.LambdaFunction import LambdaFunction
from test.DummyFactory import DummyFactory


class DummyLambdaFunction(LambdaFunction):
    def __init__(self):
        super().__init__("dummy", "Dummy lambda function")
        self._factories.add(DummyFactory())
