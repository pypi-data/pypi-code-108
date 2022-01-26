# -*- coding: utf-8 -*-
from typing import Optional, Any

from .LambdaClient import LambdaClient


class CommandableLambdaClient(LambdaClient):
    """
    Abstract client that calls commandable AWS Lambda Functions.

    Commandable services are generated automatically for :class:`ICommandable <pip_services3_commons.commands.ICommandable.ICommandable>` objects.
    Each command is exposed as action determined by "cmd" parameter.

    ### Configuration parameters ###

        - connections:
            - discovery_key:               (optional) a key to retrieve the connection from :class:`IDiscovery <pip_services3_components.connect.IDiscovery.IDiscovery>`
            - region:                      (optional) AWS region
        - credentials:
            - store_key:                   (optional) a key to retrieve the credentials from :class:`ICredentialStore <pip_services3_components.auth.ICredentialStore.ICredentialStore>`
            - access_id:                   AWS access/client id
            - access_key:                  AWS access/client id
        - options:
            - connect_timeout:             (optional) connection timeout in milliseconds (default: 10 sec)

    ### References ###
        - `*:logger:*:*:1.0`           (optional) :class:`ILogger <pip_services3_components.log.ILogger.ILogger>` components to pass log messages
        - `*:counters:*:*:1.0`         (optional) :class:`ICounters <pip_services3_components.count.ICounters.ICounters>` components to pass collected measurements
        - `*:discovery:*:*:1.0`        (optional) :class:`IDiscovery <pip_services3_components.connect.IDiscovery.IDiscovery>` services to resolve connection
        - `*:credential-store:*:*:1.0`  (optional) Credential stores to resolve credentials

    See :class:`LambdaFunction <pip_services3_aws.containers.LambdaFunction.LambdaFunction>`

    Example:

        .. code-block:: python

            class MyLambdaClient(CommandableLambdaClient, IMyClient):
                ...
    
                def get_data(self, correlation_id: str, id: str) -> Any
                    return this.callCommand("get_data", correlation_id, { 'id': id })

            ...
        
            client = MyLambdaClient()
            client.configure(ConfigParams.from_еuples(
                "connection.region", "us-east-1",
                "connection.access_id", "XXXXXXXXXXX",
                "connection.access_key", "XXXXXXXXXXX",
                "connection.arn", "YYYYYYYYYYYYY"
            ))

            result = client.get_data("123", "1")
            ...
    """

    def __init__(self, name: str):
        """
        Creates a new instance of this client.

        :param name: a service name.
        """
        super().__init__()
        self.__name = name

    def call_command(self, cmd: str, correlation_id: Optional[str], params: dict) -> Any:
        """
        Calls a remote action in AWS Lambda function.
        The name of the action is added as "cmd" parameter
        to the action parameters.

        :param cmd: an action name
        :param correlation_id: (optional) transaction id to trace execution through call chain.
        :param params: command parameters.
        :return: action result.
        """
        command = self.__name + '.' + cmd
        timing = self._instrument(correlation_id, command)
        try:
            result = self._call(command, correlation_id, params)
            timing.end_timing()
            return result
        except Exception as e:
            timing.end_timing(e)
            raise e
