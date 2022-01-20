import os
from logging import Logger
from penvy.setup.SetupStepInterface import SetupStepInterface


class ProjectRootDirSetter(SetupStepInterface):
    def __init__(
        self,
        project_root_path: str,
        logger: Logger,
    ):
        self._project_root_path = project_root_path
        self._logger = logger

    def run(self):
        self._logger.info(f"Changing current working directory to {self._project_root_path}")
        os.chdir(self._project_root_path)

    def get_description(self):
        return "Change current working directory to project root path"

    def should_be_run(self) -> bool:
        return not os.getcwd() == self._project_root_path
