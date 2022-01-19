import json
from pathlib import Path
from typing import Any, Dict, List, Union

import yaml
from dotenv import load_dotenv


def load_file(path: Union[Path, str]) -> Dict[str, Any]:
    """
    Loads fields from a file into a dictionary.

    Args:
        path: Path to the file to load.
    """
    path = Path(path)

    if not path.is_file():
        raise ValueError(f'{path=} is not exists.')

    if path.suffix == '.json':
        with open(path, mode='r') as file:
            return json.load(file)

    if path.suffix == '.yaml':
        with open(path, mode='r') as file:
            return yaml.safe_load(file)

    raise ValueError(f'{path=} is not a supported file.')


def load_env_files(paths: List[Union[Path, str]]) -> None:
    """
    Loads '.env' files in the format of '<name>=<value>' into the `os.environ` dictionary.

    Args:
        paths: List of file paths.
    """
    for path in paths:
        load_dotenv(path)
