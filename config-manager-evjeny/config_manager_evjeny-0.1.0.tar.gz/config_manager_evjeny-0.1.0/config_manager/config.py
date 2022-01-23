import os
from argparse import ArgumentParser
import json
from typing import Optional


class Config:
    """
    Class to define required variables, their types and default values, for example:

    class BotConfig(Config):
        restart_on_failure: bool
        bot_name: str = "Example bot"

    """

    @staticmethod
    def _is_variable_name(name: str) -> bool:
        return not name.startswith("_")

    def __repr__(self):
        return "\n".join(
            f"{v} = {getattr(self, v)}" for v in filter(self._is_variable_name, dir(self))
        )


def parse_env(config: Config, prefix: Optional[str] = None):
    for variable_name, variable_type in config.__annotations__.items():
        expected_name = prefix + variable_name if prefix else variable_name
        if expected_name not in os.environ:
            continue

        variable_value = variable_type(os.environ.get(expected_name))
        setattr(config, variable_name, variable_value)


def parse_arguments(config: Config, parser_description: str):
    parser = ArgumentParser(parser_description)
    for variable_name, variable_type in config.__annotations__.items():
        parser.add_argument(f"--{variable_name}", type=variable_type, required=False)

    args, unknown = parser.parse_known_args()
    for variable_name in config.__annotations__.keys():
        parsed_value = getattr(args, variable_name)
        if parsed_value:
            setattr(config, variable_name, parsed_value)


def parse_json(config: Config, json_path: str):
    with open(json_path) as f:
        json_variables = json.load(f)
        assert isinstance(json_variables, dict), "json config must be dictionary!"

    for variable_name, variable_type in config.__annotations__.items():
        if variable_name not in json_variables:
            continue

        setattr(config, variable_name, variable_type(json_variables.get(variable_name)))
