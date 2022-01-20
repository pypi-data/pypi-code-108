from pathlib import Path
from typing import Union


class PandoraModel:
    """PandoraModel contains information about a machine learning model."""

    language: str
    name: str
    client: str
    version: str
    unzip: bool
    filename: str
    path: Union[Path, None]

    def __init__(
        self,
        type: str,
        language: str,
        size: Union[str, None],
        name: str,
        client: str,
        version: str,
        path: Union[Path, None],
        filename: str = None
    ):
        self.language = language
        self.type = type
        self.size = size
        self.name = name
        self.client = client
        self.version = version
        #self.unzip = unzip
        #self.filename = filename
        self.path = path
        self.filename = filename

    def __eq__(self, other):
        return (
            self.type == other.type
            and self.language == other.language
            and self.size == other.size
            and self.name == other.name
            and self.client == other.client
            and self.version == other.version
            #and self.unzip == other.unzip
            #and self.path == other.path
        )

    def __ne__(self, other):
        return (
            self.type != other.type
            or self.language != other.language
            or self.size != other.size
            or self.name != other.name
            or self.client != other.client
            or self.version != other.version
            #or self.unzip != other.unzip
            #or self.filename != other.filename
        )
