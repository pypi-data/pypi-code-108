from pathlib import Path
from typing import Any, Union

from config_source import ConfigSource
from pydantic.main import BaseModel


class ConfigProperty(BaseModel):
    """
    Holds details of a single configuration variable and its value.
    """
    name: str
    value: Any
    origin_value: Any
    source_name: str
    source_type: ConfigSource
    source_location: Union[str, Path]

    def __init__(self, value: Any, **kwargs):
        try:
            origin_value = kwargs.pop('origin_value')
        except KeyError:
            origin_value = value
        super().__init__(value=value, origin_value=origin_value, **kwargs)
