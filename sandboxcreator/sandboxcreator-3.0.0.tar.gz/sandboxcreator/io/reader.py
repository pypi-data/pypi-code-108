import os
from pathlib import Path
from typing import Union, List, Dict

import yaml


class Reader:
    """Static methods for reading from files"""

    @staticmethod
    def open_yaml(file_path: Path) -> Union[List, Dict]:
        """Open a yaml file and return its content"""
        try:
            with file_path.open() as input_file:
                return yaml.safe_load(input_file)
        except yaml.YAMLError:
            raise IOError(f"Could not parse yaml file {file_path}.")
        except IOError:
            raise IOError(f"Could not open yaml file {file_path}.")

    @staticmethod
    def file_exists(file: Path) -> bool:
        """Check if the given file exists

        :param file: path to a file
        """

        return os.path.isfile(file)

    @staticmethod
    def dir_exists(directory: Path) -> bool:
        """Check if the given directory exists

        :param directory: path to a directory
        """

        return os.path.isdir(directory)
