# -*- coding: utf-8 -*-
import os
import signal
import sys
from abc import ABC
from typing import Dict, Any, Optional, List, Callable

from pip_services3_commons.config import ConfigParams
from pip_services3_commons.errors import UnknownException, BadRequestException
from pip_services3_commons.refer import DependencyResolver, IReferences, Descriptor
from pip_services3_commons.validate import Schema
from pip_services3_components.count import CompositeCounters
from pip_services3_components.log import ConsoleLogger
from pip_services3_components.trace.CompositeTracer import CompositeTracer
from pip_services3_container import Container
from pip_services3_rpc.services.InstrumentTiming import InstrumentTiming

from pip_services3_aws.services import ILambdaService


class LambdaFunction(Container, ABC):
    """
    Abstract AWS Lambda function, that acts as a container to instantiate and run components
    and expose them via external entry point.

    When handling calls "cmd" parameter determines which what action shall be called, while
    other parameters are passed to the action itself.

    Container configuration for this Lambda function is stored in `"./config/config.yml"` file.
    But this path can be overriden by `CONFIG_PATH` environment variable.

    ### References ###
        - `*:logger:*:*:1.0`                   (optional) :class:`ContextInfo <pip_services3_components.log.ILogger.ILogger>` components to pass log messages
        - `*:counters:*:*:1.0`                 (optional) :class:`ContextInfo <pip_services3_components.count.ICounters.ICounters>` components to pass collected measurements
        - `*:service:lambda:*:1.0`              (optional) :class:`ILambdaService <pip_services3_aws.services.ILambdaService.ILambdaService>` services to handle action requests
        - `*:service:commandable-lambda:*:1.0`  (optional) :class:`ILambdaService <pip_services3_aws.services.ILambdaService.ILambdaService>` services to handle action requests

    See :class:`ILambdaService <pip_services3_aws.clients.LambdaClient.LambdaClient>`

    Example:

    .. code-block:: python

        class MyLambdaFunction(LambdaFunction):
            def __init__(self):
                super().__init__("mygroup", "MyGroup lambda function")


        lambda = MyLambdaFunction()

        service.run();
        print("MyLambdaFunction is started")
    """

    def __init__(self, name: str = None, description: str = None):
        """
        Creates a new instance of this lambda function.

        :param name: (optional) a container name (accessible via ContextInfo)
        :param description: (optional) a container description (accessible via ContextInfo)
        """
        super().__init__(name, description)

        self._logger: ConsoleLogger = ConsoleLogger()

        # The dependency resolver.
        self._dependency_resolver: DependencyResolver = DependencyResolver()

        # The performanc counters.
        self._counters: CompositeCounters = CompositeCounters()

        # The tracer.
        self._tracer: CompositeTracer = CompositeTracer()

        # The map of registred validation schemas.
        self._schemas: Dict[str, Schema] = {}

        # The map of registered actions.
        self._actions: Dict[str, Any] = {}

        # The default path to config file.
        self._config_path: str = './config/config.yml'

    def __get_config_path(self) -> str:
        return os.getenv('CONFIG_PATH', self._config_path)

    def __get_parameters(self) -> ConfigParams:
        return ConfigParams.from_value(dict(os.environ))

    def __capture_exit(self, correlation_id: Optional[str]):
        self._logger.info(correlation_id, "Press Control-C to stop the microservice...")

        # Activate graceful exit
        signal.signal(signal.SIGINT, lambda signum, frame: sys.exit())

        # Gracefully shutdown
        def shutdown(signum, frame):
            self.close(correlation_id)
            self._logger.info(correlation_id, 'Goodbye!' or sys.exit(0))
            sys.exit(0)

        signal.signal(signal.SIGTERM, shutdown)

    def set_references(self, references: IReferences):
        """
        Sets references to dependent components.

        :param references: references to locate the component dependencies.
        """
        super(LambdaFunction, self).set_references(references)
        self._counters.set_references(references)
        self._dependency_resolver.set_references(references)

        self.register()

    def open(self, correlation_id: Optional[str]):
        """
        Opens the component.

        :param correlation_id: (optional) transaction id to trace execution through call chain.
        """
        if self.is_open():
            return

        super(LambdaFunction, self).open(correlation_id)
        self._register_services()

    def _instrument(self, correlation_id: Optional[str], name: str) -> InstrumentTiming:
        """
        Adds instrumentation to log calls and measure call time.
        It returns a InstrumentTiming object that is used to end the time measurement.

        Note: This method has been deprecated. Use LambdaService instead.

        :param correlation_id: (optional) transaction id to trace execution through call chain.
        :param name: a method name.
        :return: object to end the time measurement.
        """
        self._logger.trace(correlation_id, "Executing %s method", name)
        self._counters.increment_one(name + ".exec_count")

        counter_timing = self._counters.begin_timing(name + '.exec_time')
        trace_timing = self._tracer.begin_trace(correlation_id, name, None)
        return InstrumentTiming(correlation_id, name, "exec",
                                self._logger, self._counters, counter_timing, trace_timing)

    def run(self):
        """
        Runs this lambda function, loads container configuration,
        instantiate components and manage their lifecycle,
        makes this function ready to access action calls.

        """
        correlation_id = self._info.name

        path = self.__get_config_path()
        parameters = self.__get_parameters()
        self.read_config_from_file(correlation_id, path, parameters)

        self.__capture_exit(correlation_id)
        self.open(correlation_id)

    def register(self):
        """
        Registers all actions in this lambda function.

        Note: Overloading of this method has been deprecated. Use LambdaService instead.
        """

    def _register_services(self):
        """
        Registers all lambda services in the container.
        """
        # Extract regular and commandable Lambda services from references
        services: List[ILambdaService] = self._references.get_optional(
            Descriptor("*", "service", "lambda", "*", "*")
        )

        cmd_services: List[ILambdaService] = self._references.get_optional(
            Descriptor("*", "service", "commandable-lambda", "*", "*")
        )

        services.extend(cmd_services)

        # Register actions defined in those services
        for service in services:
            # Check if the service implements required interface
            if callable(service.get_actions()):
                continue
            actions = service.get_actions()
            for action in actions:
                self._register_action(action.cmd, action.schema, action.action)

    def _register_action(self, cmd: str, schema: Optional[Schema], action: Callable[[dict], Any]):
        """
        Registers an action in this lambda function.

        Note: This method has been deprecated. Use LambdaService instead.

        :param cmd: a action/command name.
        :param schema: a validation schema to validate received parameters.
        :param action: an action function that is called when action is invoked.
        """
        if cmd == '':
            raise UnknownException(None, 'NO_COMMAND', 'Missing command')

        if action is None:
            raise UnknownException(None, 'NO_ACTION', 'Missing action')

        if action == 'function':
            raise UnknownException(None, 'ACTION_NOT_FUNCTION', 'Action is not a function')

        if hasattr(self._actions, cmd):
            raise UnknownException(None, 'DUPLICATED_ACTION', f"{cmd} action already exists")

        # Hack!!! Wrapping action to preserve prototyping context
        def action_curl(params):
            # Perform validation
            if schema is not None:
                correlation_id = params.get('correlaton_id')
                schema.validate_and_throw_exception(correlation_id, params, False)

            # Todo: perform verification?
            return action(params)

        self._actions[cmd] = action_curl

    def _execute(self, event: dict) -> Any:
        """
        Executes this AWS Lambda function and returns the result.
        This method can be overloaded in child classes
        if they need to change the default behavior

        :param event: event the event parameters (or function arguments)
        :return: the result of the function execution.
        """
        cmd: str = event.get('cmd')
        correlation_id = event.get('correlation_id')

        if cmd is None:
            raise BadRequestException(
                correlation_id,
                'NO_COMMAND',
                'Cmd parameter is missing'
            )

        action: Callable[[dict], Any] = self._actions.get(cmd)

        if action is None:
            raise BadRequestException(
                correlation_id,
                'NO_ACTION',
                'Action ' + cmd + ' was not found'
            ).with_details('command', cmd)

        return action(event)

    def __handler(self, event: dict) -> Any:
        # If already started then execute
        if self.is_open():
            return self._execute(event)

        # Start before execute
        self.run()
        return self._execute(event)

    def get_handler(self) -> Callable[[dict], Any]:
        """
        Gets entry point into this lambda function.

        :return: an incoming event object with invocation parameters.
        """

        # Return plugin function
        return lambda event: self.__handler(event)

    def act(self, params: dict) -> Any:
        """
        Calls registered action in this lambda function.
        "cmd" parameter in the action parameters determin
        what action shall be called.

        This method shall only be used in testing.

        :param params: action parameters.
        """
        return self.get_handler()(params)
