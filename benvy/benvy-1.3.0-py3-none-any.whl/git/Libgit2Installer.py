from logging import Logger
import platform
from penvy.setup.SetupStepInterface import SetupStepInterface
from penvy.shell.runner import run_shell_command


class Libgit2Installer(SetupStepInterface):
    def __init__(
        self,
        logger: Logger,
    ):
        self._logger = logger

    def get_description(self):
        return "Install libgit2 from brew to support git-based Bricksflow features"

    def run(self):
        # pygit2 vs. libgit2 versions compatibility matrix: https://www.pygit2.org/install.html#version-numbers
        run_shell_command("brew install libgit2", shell=True)

        self._logger.info("Installing libgit2")

    def should_be_run(self) -> bool:
        return platform.system() == "Darwin"
