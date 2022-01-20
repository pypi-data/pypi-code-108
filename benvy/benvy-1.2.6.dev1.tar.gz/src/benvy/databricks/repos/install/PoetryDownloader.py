import urllib
from pathlib import Path
from logging import Logger
from penvy.setup.SetupStepInterface import SetupStepInterface


class PoetryDownloader(SetupStepInterface):
    def __init__(
        self,
        poetry_version: str,
        download_url: str,
        download_path: str,
        logger: Logger,
    ):
        self._poetry_version = poetry_version
        self._download_url = download_url
        self._download_path = download_path
        self._logger = logger

    def run(self):
        self._logger.info(f"Downloading poetry {self._poetry_version}")
        Path(self._download_path).parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(self._download_url, self._download_path)

    def get_description(self):
        return f"Download poetry {self._poetry_version}"

    def should_be_run(self) -> bool:
        return not Path(self._download_path).exists()
