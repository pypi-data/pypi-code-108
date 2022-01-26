# -*- coding: utf-8 -*-
from abc import ABC
from typing import List, Any, Optional, Callable

from pip_services3_commons.config import IConfigurable, ConfigParams
from pip_services3_commons.errors import BadRequestException
from pip_services3_commons.refer import IReferenceable, DependencyResolver, IReferences
from pip_services3_commons.run import IOpenable
from pip_services3_commons.validate import Schema
from pip_services3_components.count import CompositeCounters
from pip_services3_components.log import CompositeLogger
from pip_services3_components.trace.CompositeTracer import CompositeTracer
from pip_services3_rpc.services.InstrumentTiming import InstrumentTiming

from .ILambdaService import ILambdaService
from .LambdaAction import LambdaAction


class LambdaService(ILambdaService, IOpenable, IConfigurable, IReferenceable, ABC):
    """
    Abstract service that receives remove calls via AWS Lambda protocol.

    This service is intended to work inside LambdaFunction container that
    exploses registered actions externally.

    ### Configuration parameters ###
        - dependencies:
            - controller:            override for Controller dependency

    ### References ###
        - `*:logger:*:*:1.0`           (optional) :class:`ILogger <pip_services3_components.log.ILogger.ILogger>` components to pass log messages
        - `*:counters:*:*:1.0`         (optional) :class:`ICounters <pip_services3_components.count.ICounters.ICounters>` components to pass collected measurements

    Example:

    .. code-block:: python

        class MyLambdaService(LambdaService):
            _controller: IMyController
           ...

           def __init__(self):
                super().__init__('v1.myservice')
                self._dependency_resolver.put(
                    "controller",
                    Descriptor("mygroup","controller","*","*","1.0")
                )

           def set_references(self, references: IReferences):
              super().set_references(references)
              self._controller = self._dependency_resolver.get_required("controller")
           

           def __action(self, params):
                correlation_id = params.correlation_id
                id = params.id
                return self._controller.get_my_data(correlationId, id)

           def register(self):
               self.register_action("get_my_data", None, __action)

               ...
           

        service = MyLambdaService()
        service.configure(ConfigParams.from_tuples(
            "connection.protocol", "http",
            "connection.host", "localhost",
            "connection.port", 8080
        ))

        service.set_references(References.from_tuples(
            Descriptor("mygroup","controller","default","default","1.0"), controller
        ))

        service.open("123")
        print("The GRPC service is running on port 8080")

    """

    def __init__(self, name: str = None):
        self.__name: str = name
        self.__actions: List[LambdaAction] = []
        self.__interceptors: List[Any] = []
        self.__opened: bool = False

        # The dependency resolver.
        self._dependency_resolver: DependencyResolver = DependencyResolver()

        # The logger.
        self._logger: CompositeLogger = CompositeLogger()

        # The performance counters.
        self._counters: CompositeCounters = CompositeCounters()

        # The tracer.
        self._tracer: CompositeTracer = CompositeTracer()

    def configure(self, config: ConfigParams):
        """
        Configures component by passing configuration parameters.

        :param config: configuration parameters to be set.
        """
        self._dependency_resolver.configure(config)

    def set_references(self, references: IReferences):
        """
        Sets references to dependent components.

        :param references: references to locate the component dependencies.
        """
        self._logger.set_references(references)
        self._counters.set_references(references)
        self._tracer.set_references(references)
        self._dependency_resolver.set_references(references)

    def get_actions(self) -> List[LambdaAction]:
        """
        Get all actions supported by the service.

        :return: an array with supported actions.
        """
        return self.__actions

    def _instrument(self, correlation_id: Optional[str], name: str) -> InstrumentTiming:
        """
        Adds instrumentation to log calls and measure call time.
        It returns a Timing object that is used to end the time measurement.

        :param correlation_id: (optional) transaction id to trace execution through call chain.
        :param name: a method name.
        :return: Timing object to end the time measurement.
        """
        self._logger.trace(correlation_id, "Executing %s method", name)
        self._counters.increment_one(name + ".exec_count")

        counter_timing = self._counters.begin_timing(name + ".exec_time")
        trace_timing = self._tracer.begin_trace(correlation_id, name, None)
        return InstrumentTiming(correlation_id, name, 'exec', self._logger, self._counters,
                                counter_timing, trace_timing)

    def is_open(self) -> bool:
        """
        Checks if the component is opened.

        :return: true if the component has been opened and false otherwise.
        """
        return self.__opened

    def open(self, correlation_id: Optional[str]):
        """
        Opens the component.

        :param correlation_id: (optional) transaction id to trace execution through call chain.
        """
        if self.__opened:
            return

        self.register()

        self.__opened = True

    def close(self, correlation_id: Optional[str]):
        """
        Closes component and frees used resources.

        :param correlation_id: (optional) transaction id to trace execution through call chain.
        """
        if not self.__opened:
            return

        self.__opened = False
        self.__actions = []
        self.__interceptors = []

    def _apply_validation(self, schema: Schema, action: Callable[[dict], Any]) -> Callable[[dict], Any]:

        # Create an action function

        def action_wrapper(params: dict):
            # Validate object
            if schema and params:
                # Perform validation
                correlation_id = params.get('correlation_id')
                schema.validate_and_throw_exception(correlation_id, params, False)
            result = action(params)
            return result

        return action_wrapper

    def _apply_interceptors(self, action: Callable[[Any], Any]) -> Callable[[Any], Any]:
        action_wrapper = action

        index = len(self.__interceptors) - 1
        while index >= 0:
            interceptor = self.__interceptors[index]
            action_wrapper = lambda action: lambda params: interceptor(params, action)(action_wrapper)

        return action_wrapper

    def _generate_action_cmd(self, name: str) -> str:
        cmd = name
        if self.__name is not None:
            cmd = self.__name + '.' + cmd

        return cmd

    def _register_action(self, name: str, schema: Optional[Schema], action: Callable[[Any], Any]):
        """
        Registers a action in AWS Lambda function.

        :param name: an action name
        :param schema: a validation schema to validate received parameters.
        :param action: an action function that is called when operation is invoked.
        """
        action_wrapper = self._apply_validation(schema, action)
        action_wrapper = self._apply_interceptors(action_wrapper)

        register_action: LambdaAction = LambdaAction(self._generate_action_cmd(name), schema,
                                                     lambda params: action_wrapper(params))

        self.__actions.append(register_action)

    def _register_action_with_auth(self, name: str, schema: Schema,
                                   authorize: Callable[[Any, Callable[[Any], Any]], Any], action: Callable[[Any], Any]):
        """
        Registers an action with authorization.

        :param name: an action name
        :param schema: a validation schema to validate received parameters.
        :param authorize: an authorization interceptor
        :param action: an action function that is called when operation is invoked.
        """
        action_wrapper = self._apply_validation(schema, action)

        # Add authorization just before validation
        action_wrapper = lambda call: authorize(call, action_wrapper)

        action_wrapper = self._apply_interceptors(action_wrapper)

        register_action: LambdaAction = LambdaAction(self._generate_action_cmd(name), schema,
                                                     lambda params: action_wrapper(params))

    def _register_interceptor(self, action: Callable[[Any, Callable[[Any], Any]], Any]):
        """
        Registers a middleware for actions in AWS Lambda service.

        :param action: an action function that is called when middleware is invoked.
        """
        self.__interceptors.append(action)

    def register(self):
        """
        Registers all service routes in HTTP endpoint.

        This method is called by the service and must be overriden
        in child classes.
        """

    def act(self, params: dict) -> Any:
        """
        Calls registered action in this lambda function.
        "cmd" parameter in the action parameters determin
        what action shall be called.

        This method shall only be used in testing.

        :param params: action parameters.
        """
        cmd = params.get('cmd')
        correlation_id = params.get('correlation_id')

        if cmd is None:
            raise BadRequestException(
                correlation_id,
                'NO_COMMAND',
                'Cmd parameter is missing'
            )

        find_action = list(filter(lambda a: a.cmd == cmd, self.__actions))
        action: LambdaAction = None if len(find_action) <= 0 else find_action[0]
        if action is None:
            raise BadRequestException(
                correlation_id,
                'NO_ACTION',
                'Action ' + cmd + ' was not found'
            ).with_details('command', cmd)

        return action.action(params)
