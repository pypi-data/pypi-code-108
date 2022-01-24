# Built in modules
import csv
import json
from pkgutil import get_data
import logging
from pathlib import Path
import os
import sys
import zipfile
from typing import Any, List, Optional


# Third Party modules
import yaml

# Project Specific Modules
logger = logging.getLogger(__name__)

YAML_EXTENSIONS = ['.yml', '.yaml']
JSON_EXTENSIONS = [".json", ".jsonl", ".geojson"]


def load_data(file_path: Path,
              skip_loaders: bool = False,
              content_type: str = "utf-8") -> Any:

    if not file_path.is_file():
        return None
    fh = file_path.open(mode='rb')
    data_content = fh.read()
    fh.close()

    if not data_content:
        return None

    if skip_loaders:
        return data_content.decode(content_type)

    if file_path.suffix in ['.zip']:
        return load_data_zip(file_path, content_type)

    if file_path.suffix.lower() in ['.csv']:
        return load_data_csv(file_path)
    if file_path.suffix.lower() in YAML_EXTENSIONS:
        return load_data_yaml(file_path)
    if file_path.suffix.lower() in JSON_EXTENSIONS:
        return load_data_json(data_content.decode(content_type))

    return data_content


def load_data_zip(file_path: Path,
                  content_type: str = "utf-8"):

    with zipfile.ZipFile(file_path) as zf:
        zipfiles = zf.namelist()
        if len(zipfiles) == 1:
            content = zf.open(zipfiles[0]).read()

            if type(content) is bytes:
                content = content.decode(content_type)
            return {"filename": zipfiles[0], "content": content}
        if len(zipfiles) != 1:
            raise Exception(
                "Zero or more than one file in zip file. Have {}"
                    .format(len(zipfiles))
            )


def load_data_csv(file_path: Path):
    """
    Load a csv file
    :param file_path:
    :return:
    """
    # TODO
    logger.warning("load_data_csv not implemented")
    return None


def load_data_yaml(yaml_path: Path):
    with yaml_path.open(mode='r') as f:
        return yaml.load(f, Loader=yaml.FullLoader)


def load_data_json(file_content: str):
    return json.loads(file_content)


