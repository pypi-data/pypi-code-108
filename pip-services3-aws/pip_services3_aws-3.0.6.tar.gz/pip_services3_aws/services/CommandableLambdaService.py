# -*- coding: utf-8 -*-
from abc import ABC

from pip_services3_commons.commands import CommandSet, ICommandable
from pip_services3_commons.run import Parameters

from .LambdaService import LambdaService


class CommandableLambdaService(LambdaService, ABC):
    """
        Abstract service that receives commands via AWS Lambda protocol
        to operations automatically generated for commands defined in :class:`ICommandable <pip_services3_commons.commands.ICommandable.ICommandable>` components.
        Each command is exposed as invoke method that receives command name and parameters.

        Commandable services require only 3 lines of code to implement a robust external
        Lambda-based remote interface.

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
            
            class MyCommandableLambdaService(CommandableLambdaService):
                def __init__(self):
                    super().__init__()
                    self._dependency_resolver.put(
                        "controller",
                        Descriptor("mygroup","controller","*","*","1.0")
                  )

            service = MyCommandableLambdaService()
            service.set_references(References.from_tuples(
                Descriptor("mygroup","controller","default","default","1.0"), controller
            ))

            service.open("123")
            print("The AWS Lambda service is running")
    """

    def __init__(self, name: str):
        """
        Creates a new instance of the service.

        :param name: a service name.
        """
        super().__init__(name)
        self._dependency_resolver.put('controller', 'none')
        self.__command_set: CommandSet = None

    def register(self):
        """
        Registers all actions in AWS Lambda function.
        """

        def wrapper(command):
            # wrapper for passing context
            def action(params):
                correlation_id = None if params is None else params.get('correlation_id')

                args = Parameters.from_value(params)
                if correlation_id:
                    args.remove('correlation_id')

                timing = self._instrument(correlation_id, name)
                try:
                    return command.execute(correlation_id, args)
                except Exception as e:
                    timing.end_failure(e)
                finally:
                    timing.end_timing()

            return action

        controller: ICommandable = self._dependency_resolver.get_one_required('controller')
        self.__command_set = controller.get_command_set()

        commands = self.__command_set.get_commands()
        for index in range(len(commands)):
            command = commands[index]
            name = command.get_name()

            self._register_action(name, None, wrapper(command))
