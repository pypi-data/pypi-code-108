import os
import urllib.request
import platform
from logging import Logger
from penvy.setup.SetupStepInterface import SetupStepInterface


class WinutilsDownloader(SetupStepInterface):
    def __init__(
        self,
        venv_dir: str,
        winutils_url: str,
        logger: Logger,
    ):
        self._winutils_dir = venv_dir + "/hadoop/bin"
        self._winutils_executable_path = self._winutils_dir + "/winutils.exe"
        self._winutils_url = winutils_url
        self._logger = logger

    def get_description(self):
        return "Download Hadoop's winutils.exe"

    def run(self):
        self._logger.info("Downloading Hadoop winutils.exe")

        os.makedirs(self._winutils_dir, exist_ok=True)

        urllib.request.urlretrieve(self._winutils_url, self._winutils_executable_path)

    def should_be_run(self) -> bool:
        return platform.system() == "Windows" and not os.path.isfile(self._winutils_executable_path)
