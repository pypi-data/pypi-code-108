"""Configuration file loader and validation functions."""
from abc import abstractmethod, ABC
from datetime import datetime
from logging.config import dictConfig
import os
from pathlib import Path
from typing import Any, Collection, Mapping, Optional, Sequence, Union
import yaml

from flatten_dict import flatten
from pyspark.sql import SparkSession

from ons_utils._typing import PathLike
# import .validation
from ons_utils.generic import (
    fill_tuples,
    fill_tuple_keys,
    get_key_value_pairs,
    is_non_string_sequence,
    list_convert,
    tuple_convert,
)


class ConfigFormatError(Exception):
    """Exception raised when given config YAML is not in mapping format."""

    def __init__(self):
        """Init the ConfigFormatError."""
        super().__init__("attributes or config yaml must be a mapping")


class Config:
    """Base class for config files."""

    def __init__(
        self,
        filename: str,
        subdir: Optional[str] = None,
        to_unpack: Optional[Sequence[str]] = None,
    ):
        """Initialise the Config class.

        Parameters
        ----------
        filename : str,
            The filename of the config file without the YAML extension.
        subdir : str, optional
            The subdirectory within the config directory that contains
            the config file.
        to_unpack : sequence of str
            A list of keys that contain mappings to unpack. The mappings
            at given keys will be set as new attributes directly, in
            addition to the mapping being added as a normal attribute.
        """
        self.name = filename
        self.config_path = self.get_config_path(subdir)
        self.set_attrs(self.load_config(), to_unpack)

    def get_config_dir(self) -> Path:
        """Get the config directory from possible locations.

        Looks first to see if the environment variable CPRICES_CONFIG
        is set. If not cycles through current working directory, home
        directory, and cprices directories until it finds a folder
        called config which it returns.

        Returns
        -------
        Path
            The config directory.
        """
        config_dir_path_env = os.getenv("CPRICES_CONFIG")
        if config_dir_path_env:
            return Path(config_dir_path_env)

        for loc in (
            # This location is where the config is stored currently.
            Path.home().joinpath('cprices', 'cprices'),
            Path.home().joinpath('cprices'),
            Path.home(),
            Path.cwd(),
        ):
            if loc.joinpath('config').exists():
                return loc.joinpath('config')

    def get_config_path(self, subdir: Optional[str] = None) -> Path:
        """Return the path to the config file.

        Parameters
        ----------
        subdir : str, optional
            The subdirectory within the config directory that contains
            the config file.
        """
        filename = self.name + '.yaml'
        to_join = [filename] if not subdir else [subdir, filename]
        return self.get_config_dir().joinpath(*to_join)

    def load_config(self):
        """Load the config file."""
        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f)

    def update(self, attrs: Mapping[str, Any]):
        """Update the attributes."""
        for key, value in attrs.items():
            setattr(self, key, value)

    def set_attrs(
        self,
        attrs: Mapping[str, Any],
        to_unpack: Optional[Sequence[str]] = None,
    ):
        """Set attributes from given mapping using update method.

        Parameters
        ----------
        to_unpack : sequence of str
            A list of keys that contain mappings to unpack. The mappings
            at given keys will be set as new attributes directly, in
            addition to the mapping being added as a normal attribute.
        """
        if not isinstance(attrs, Mapping):
            raise ConfigFormatError

        # Initialise to_unpack as empty list if not given.
        for attr in to_unpack if to_unpack else []:
            nested_mapping = attrs[attr]
            if not isinstance(nested_mapping, Mapping):
                raise TypeError(
                    f"given attr {attr} to unpack must be a mapping"
                )
            self.update(nested_mapping)

        self.update(attrs)

    def flatten_nested_dicts(self, attrs: Sequence[str]) -> None:
        """Flatten the nested dict config for web_scraped."""
        self.update({k: flatten(getattr(self, k)) for k in attrs})

    def get_key_value_pairs(self, attrs: Sequence[str]) -> None:
        """Get the key value pairs from a dictionary as list of tuples."""
        self.update({k: get_key_value_pairs(getattr(self, k)) for k in attrs})

    def fill_tuples(
        self,
        attrs: Sequence[str],
        repeat: bool = True,
        length: int = None,
    ) -> None:
        """Fill tuples so they are all the same length."""
        self.update({
            k: fill_tuples(getattr(self, k), repeat=repeat, length=length)
            for k in attrs
        })

    def fill_tuple_keys(
        self,
        attrs: Sequence[str],
        repeat: bool = True,
        length: int = None,
    ) -> None:
        """Fill tuple keys so they are all the same length."""
        self.update({
            k: fill_tuple_keys(getattr(self, k), repeat=repeat, length=length)
            for k in attrs
        })

    def extend_attr(
        self,
        attr: str,
        extend_vals: Union[Any, Sequence[Any]],
    ) -> None:
        """Extend a list or tuple attr with the given values."""
        current_vals = getattr(self, attr)

        if not is_non_string_sequence(current_vals):
            raise AttributeError(f'attribute {attr} is not an extendable type')
        elif isinstance(current_vals, tuple):
            extend_vals = tuple_convert(extend_vals)
        elif isinstance(current_vals, list):
            extend_vals = list_convert(extend_vals)

        setattr(self, attr, current_vals + extend_vals)

    def remove_from_attr(
        self,
        attr: str,
        remove: Collection[Any],
    ) -> None:
        """Remove the given values from the attribute."""
        current_vals = getattr(self, attr)

        if not isinstance(current_vals, Collection):
            raise AttributeError(
                f'attribute {attr} is not a collection. There are no'
                ' removable items'
            )

        setattr(self, attr, [x for x in current_vals if x not in remove])

    def prepend_dir(self, attrs: Sequence[str], dir: PathLike) -> None:
        """Prepend the dirpath onto the given attrs.

        Works when the attr is a filepath or a dict of filepaths.

        Parameters
        ----------
        dir : str, bytes, os.PathLike, pathlib.Path
            A directory path to prepend to the paths in attrs.
        """
        for attr in attrs:
            current_attr = getattr(self, attr)
            if isinstance(current_attr, Mapping):
                new_attr = {
                    key: Path(dir, path).as_posix()
                    for key, path in current_attr.items()
                }
                setattr(self, attr, new_attr)
            else:
                setattr(self, attr, Path(dir, current_attr).as_posix())


class LoggingConfig:
    """Class to set logging config."""

    def __init__(self):
        """Init the logging config object."""
        self.log_id = self.create_log_id()
        self.log_dir = self.get_logs_dir()
        self.filename = f'{self.log_id}.log'
        self.full_path = self.log_dir.joinpath(self.filename).as_posix()

    def create_log_id(self) -> str:
        """Create the unique log ID from the current timestamp."""
        return 'log_' + datetime.now().strftime('%y%m%d_%H%M%S')

    def get_logs_dir(self) -> Path:
        """Return the logs directory."""
        loc = Path.home().joinpath('cprices', 'cprices')
        if loc.exists():
            return loc.joinpath('run_logs')

        return Path.home().joinpath('cprices_run_logs')

    def create_logs_dir(self) -> None:
        """Create the log directory if not already created."""
        self.get_logs_dir().mkdir(exist_ok=True)

    def set_logging_config(
        self,
        console: str,
        text_log: str,
        disable_other_loggers: bool = False,
    ) -> None:
        """Set the config for the logging module.

        Parameters
        ----------
        console : str
            Formatter ID for the console handler. Can be any string value.
        text_log : str
            Formatter for the log file handler.
        disable_other_loggers : bool, default False
            If True, disables any existing non-root loggers unless they
            or their ancestors are explicitly named in the logging
            configuration.
        """
        logging_config = {
            'version': 1,
            'loggers': {
                '': {  # root logger
                    'handlers': ['console', 'file_log'],
                    'level': 'INFO',
                    'propagate': False,
                },
            },
            'handlers': {
                'console': {
                    'class': 'logging.StreamHandler',
                    'formatter': console,
                    'level': 'INFO',
                },
                'file_log': {
                    'class': 'logging.FileHandler',
                    'formatter': text_log,
                    'level': 'DEBUG',
                    'mode': 'w',
                    'filename': self.full_path,
                },
            },
            'formatters': {
                'basic': {
                    'format': '%(message)s',
                },
                'debug': {
                    'format': '[%(asctime)s %(levelname)s - file=%(filename)s:%(lineno)d] %(message)s',
                    'datefmt': '%y/%m/%d %H:%M:%S',
                },
            },
            'disable_existing_loggers': disable_other_loggers,
        }
        dictConfig(logging_config)
