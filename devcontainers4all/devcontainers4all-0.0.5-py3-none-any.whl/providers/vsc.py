"""Visual Studio Code implementations
"""
import commentjson
from logzero import setup_logger

from ..interfaces import Configuration, DevContainer

# pylint: disable=too-few-public-methods


class Manifest(DevContainer):
    """A representation of the devcontainer.json manifest"""

    def __init__(self, configuration: Configuration) -> None:
        super().__init__()
        self.__logger = setup_logger(name="VisualStudioCodeManifest")

        self.__logger.debug(
            "Using VisualStudioCode Manifest %s ",
            configuration.location.resolve() / configuration.manifest_file,
        )

        with open(
            configuration.location.resolve() / configuration.manifest_file,
            "r",
            encoding="utf8",
        ) as manifest:
            # VSC DevContainer manifest containes commnets, the standard json module cannot be used
            self.__manifest = commentjson.load(manifest)

    def get(self, key):
        return self.__manifest[key]
