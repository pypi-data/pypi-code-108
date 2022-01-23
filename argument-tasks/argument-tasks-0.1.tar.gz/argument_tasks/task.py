import argparse
from typing import Any, Callable, Dict

import pydantic


class Value(pydantic.BaseModel):
    name: str
    type: Any
    required: bool
    description: str

    def __str__(self):
        return f"{self.name} | {self.description}"


class Task:
    class NotRunningError(Exception):
        def __init__(self, message: Any = ""):
            super().__init__("Cannot run task - %s" % (message))

    def __init__(
        self,
        parser: argparse.ArgumentParser,
        name: str,
        action: Callable,
        values: Dict[str, Any],
    ) -> None:
        """Name for task should be descriptive"""
        self.name = name
        self.action = action
        self.required_values: Dict[str, Value] = dict()
        self.non_required_values: Dict[str, Value] = dict()
        self.set_values(values)
        self.set_task_arguments(parser)

    def __eq__(self, obj: Any):
        return self.name == obj

    def __str__(self):
        values = {
            "task": self.name,
            "required_args": "\n".join(
                [str(self.required_values[key]) for key in self.required_values]
            ),
            "non_required": "\n".join(
                [str(self.non_required_values[key]) for key in self.non_required_values]
            ),
        }
        return str(values)

    def set_values(self, values: Dict[str, Any]) -> None:
        for value in values:
            value["type"] = eval(value["type"])
            value = Value.parse_obj(value)
            if value.required:
                self.required_values[value.name] = value
            else:
                self.non_required_values[value.name] = value

    def get_all_args(self) -> Dict[str, Value]:
        return {**self.required_values, **self.non_required_values}

    def set_task_arguments(self, parser: argparse.ArgumentParser) -> None:

        all_args = self.get_all_args()

        for arg in all_args:
            arg_value = all_args.get(arg)
            parser.add_argument(
                f"--{arg_value.name}",
                nargs="?",
                type=arg_value.type,
                help=arg_value.description,
            )

    def run(self, **kwargs) -> None:
        try:
            can_run = True
            for required in self.required_values:
                can_run = can_run and required in kwargs

            if can_run:
                self.action(**kwargs)
            else:
                raise Exception(
                    "Not all required args provided: %s"
                    % (
                        [
                            f"{key}: {self.required_values[key].description}"
                            for key in self.required_values
                        ]
                    )
                )
        except Exception as e:
            raise Task.NotRunningError(e)
