# -*- coding: utf-8 -*-
from typing import Optional, Any

from pip_services3_aws.clients.LambdaClient import LambdaClient


class TestLambdaClient(LambdaClient):
    def __init__(self):
        super(TestLambdaClient, self).__init__()

    def call(self, cmd: str, correlation_id: Optional[str], params: dict = None) -> Any:
        """
        Calls a AWS Lambda Function action.

        :param cmd: an action name to be called.
        :param correlation_id: (optional) transaction id to trace execution through call chain.
        :param params: (optional) action parameters.
        :return: action result.
        """
        return super()._call(cmd, correlation_id, params or {})

    def call_one_way(self, cmd: str, correlation_id: Optional[str], params: dict = None) -> Any:
        """
        Calls a AWS Lambda Function action asynchronously without waiting for response.

        :param cmd: an action name to be called.
        :param correlation_id: (optional) transaction id to trace execution through call chain.
        :param params: (optional) action parameters.
        :return: action result.
        """
        return super()._call_one_way(cmd, correlation_id, params)
