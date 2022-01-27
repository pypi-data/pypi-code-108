import sys
from pathlib import Path
from logging import Logger
from penvy.setup.SetupStepInterface import SetupStepInterface
from penvy.shell.runner import run_with_live_output


class PoetryInstaller(SetupStepInterface):
    def __init__(
        self,
        poetry_version: str,
        poetry_home: str,
        poetry_executable: str,
        poetry_archive_path: str,
        poetry_install_script_path: str,
        logger: Logger,
    ):
        self._poetry_version = poetry_version
        self._poetry_home = poetry_home
        self._poetry_executable = poetry_executable
        self._poetry_archive_path = poetry_archive_path
        self._poetry_install_script_path = poetry_install_script_path
        self._logger = logger

    def run(self):
        self._logger.info("Installing poetry")

        run_with_live_output(
            f"POETRY_HOME={self._poetry_home} {sys.executable} {self._poetry_install_script_path} --file {self._poetry_archive_path}",
            shell=True,
        )

    def get_description(self):
        return f"Install poetry {self._poetry_version}"

    def should_be_run(self) -> bool:
        return not Path(self._poetry_home).exists()
