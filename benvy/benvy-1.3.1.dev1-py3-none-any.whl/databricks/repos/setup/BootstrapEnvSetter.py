import os
from logging import Logger
from penvy.setup.SetupStepInterface import SetupStepInterface


class BootstrapEnvSetter(SetupStepInterface):
    def __init__(
        self,
        logger: Logger,
    ):
        self._logger = logger

    def run(self):
        self._logger.info("Setting DAIPE_BOOTSTRAPPED environment variable")
        os.environ["DAIPE_BOOTSTRAPPED"] = "1"

    def get_description(self):
        return "Set DAIPE_BOOTSTRAPPED environment variable"

    def should_be_run(self) -> bool:
        return "DAIPE_BOOTSTRAPPED" not in os.environ
