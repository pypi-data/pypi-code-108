import yaml
import argparse
from typing import Any, Dict, Tuple

from argument_tasks.task import Task


class Interface:

    COMMAND_ARG_NAME = "command"

    class UnloadableSourceError(Exception):
        def __init__(self, message: Any = str()):
            super().__init__("Cannot load tasks source - %s" % (message))

    class UnsetteableTaskError(Exception):
        def __init__(self, message: Any = str()):
            super().__init__("Cannot set tasks - %s" % (message))

    class NoCorrectCommandOrArgumentsException(Exception):
        def __init__(self, message: Any = str()):
            super().__init__(
                "There's a problem with command or arguments provided - %s" % (message)
            )

    class NoOrUnknownCommandException(Exception):
        def __init__(self):
            super().__init__("There was an unknown or no command provided")

    def __init__(self, source: Any, methods: Any) -> None:
        """Necessary parameters:
        source: Is a yml with information about commands with
                the following format:

                <command_name: str>:
                    action: <method_name: str>
                    values:
                        -
                            name: <arg_name: str>
                            type: <arg_type: python_class>
                            required: <whether_arg_is_required: bool>
                            description: <arg_description: str>

        methods: python module with methods called on task execution
        """
        self.parser = argparse.ArgumentParser()
        self.tasks = dict()
        self.source = source
        self.methods = methods
        self.__set_tasks_from_source()
        self.parser.add_argument(Interface.COMMAND_ARG_NAME, nargs="?")

    def __set_tasks(self, task: Dict[str, Any]) -> None:
        try:
            name = task.get("name")
            action = getattr(self.methods, task.get("action"))
            values = task.get("values")

            task = Task(self.parser, name=name, action=action, values=values)
            self.tasks[name] = task
        except Exception as e:
            raise Interface.UnsetteableTaskError(e)

    def __set_tasks_from_source(self) -> None:
        try:
            source = yaml.safe_load(self.source)
            for key in source:
                task = {"name": key, **source[key]}
                self.__set_tasks(task)
        except Exception as e:
            raise Interface.UnloadableSourceError(e)

    def get_task_and_arguments(self) -> Tuple[Task, Dict[str, Any]]:
        def delete_none_args(args: Dict[str, Any]) -> Dict[str, Any]:
            none_value_args = list()

            for key in args:
                arg = args[key]
                if arg == None:
                    none_value_args.append(key)

            for key in none_value_args:
                del args[key]

            return args

        try:
            known, rest = self.parser.parse_known_args()
            kwargs = known._get_kwargs()
            args = dict()

            for arg in kwargs:
                key, value = arg
                args[key] = value

            command_arg = args[Interface.COMMAND_ARG_NAME]

            del args[Interface.COMMAND_ARG_NAME]

            if command_arg in self.tasks:
                return self.tasks[command_arg], delete_none_args(args)
            else:
                raise Interface.NoOrUnknownCommandException()

        except Exception as e:
            raise Interface.NoCorrectCommandOrArgumentsException(e)

    def run(self) -> None:
        task, args = self.get_task_and_arguments()
        task.run(**args)
