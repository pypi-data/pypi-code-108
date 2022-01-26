import sys
from typing import Any

import yaml

from pytestapilib.core.log import log
from pytestapilib.core.system import ProjectVariables


class FileReader:
    def __init__(self, file_path: str):
        self.file_path = file_path
        if sys.platform.startswith('win32'):
            self.file_path = file_path.replace('/', '\\')

    def read_yml(self) -> Any:
        file_path = ProjectVariables.PROJECT_ROOT_DIR + self.file_path
        log.info(f'Reading {file_path}')
        with open(file_path, encoding='UTF-8') as stream:
            return yaml.safe_load(stream)
