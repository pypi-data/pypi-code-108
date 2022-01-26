from collections import namedtuple
import os
from typing import Iterable

from .errors import AporiaError

ConfigVar = namedtuple("ConfigVar", ["name", "env_var", "default_value", "cast_func"])


def _str_to_bool(value: str) -> bool:
    return value.lower() == "true"


REQUIRED_SETTINGS = [
    ConfigVar("token", "APORIA_TOKEN", None, str),
    ConfigVar("host", "APORIA_HOST", "app.aporia.com", str),
    ConfigVar("environment", "APORIA_ENVIRONMENT", None, str),
]
OPTIONAL_SETTINGS = [
    ConfigVar("port", "APORIA_PORT", 443, int),
    ConfigVar("verbose", "APORIA_VERBOSE", False, _str_to_bool),
    ConfigVar("throw_errors", "APORIA_THROW_ERRORS", False, _str_to_bool),
    ConfigVar("debug", "APORIA_DEBUG", False, _str_to_bool),
    ConfigVar("http_timeout_seconds", "APORIA_HTTP_TIMEOUT_SECONDS", 30, int),
]
ALL_SETTINGS = [*REQUIRED_SETTINGS, *OPTIONAL_SETTINGS]


class Config:
    """Configuration manager."""

    def __init__(self, **kwargs):
        """Initializes a config object.

        Args:
            kwargs: setting overrides.
        """
        settings = self._get_settings_from_env_vars(ALL_SETTINGS)
        overrides = {name: value for name, value in kwargs.items() if value is not None}
        settings.update(overrides)

        self._validate_required_settings(settings, REQUIRED_SETTINGS)

        # This is mostly here for auto-completion and type checks
        # We could set these in a loop using setattr instead
        self.token = settings["token"]
        self.host = settings["host"]
        self.environment = settings["environment"]
        self.port = settings["port"]
        self.verbose = settings["verbose"]
        self.throw_errors = settings["throw_errors"]
        self.debug = settings["debug"]
        self.http_timeout_seconds = settings["http_timeout_seconds"]

        # Constant values - we keep those here to make overriding them in the tests easier.
        # speed and our expected rate for inserting a prediction
        self.queue_batch_size = 4000
        self.queue_flush_interval = 5
        self.queue_max_size = 500000

        self._validate_environment(self.environment)

    @staticmethod
    def _get_settings_from_env_vars(requested_settings: Iterable[ConfigVar]) -> dict:
        settings = {}

        for config_var in requested_settings:
            value = os.environ.get(config_var.env_var)
            if value is not None:
                settings[config_var.name] = config_var.cast_func(value)
            elif config_var.default_value is not None:
                settings[config_var.name] = config_var.default_value

        return settings

    @staticmethod
    def _validate_required_settings(settings: dict, required_settings: Iterable[ConfigVar]):
        for config_var in required_settings:
            if config_var.name not in settings:
                raise AporiaError(
                    "Required setting '{}' was not defined - pass it to aporia.init or "
                    "define the APORIA_{} environment variable.".format(
                        config_var.name, config_var.env_var
                    )
                )

    @staticmethod
    def _validate_environment(environment: str):
        if len(environment) == 0:
            raise AporiaError("Environment string must be non-empty.")
