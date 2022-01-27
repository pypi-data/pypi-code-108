import sys
from logging import Logger
from penvy.setup.SetupStepInterface import SetupStepInterface


class SysPathAppender(SetupStepInterface):
    def __init__(
        self,
        project_root_path: str,
        logger: Logger,
    ):
        self._project_root_path = project_root_path
        self._logger = logger

    def run(self):
        self._logger.info(f"Appending {self._project_root_path}/src to sys path")
        sys.path.append(f"{self._project_root_path}/src")

    def get_description(self):
        return "Append project src path to sys path"

    def should_be_run(self) -> bool:
        return f"{self._project_root_path}/src" not in sys.path
