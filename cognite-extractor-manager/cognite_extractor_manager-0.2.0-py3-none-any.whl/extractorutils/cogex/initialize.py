#  Copyright 2021 Cognite AS
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import os

import requests

from cognite.extractorutils.cogex.io import get_git_user, prompt

pyproject_template = """
[tool.poetry]
name = "{name}"
version = "1.0.0"
description = "{description}"
authors = ["{author}"]

[tool.black]
line-length = 120
target_version = ['py37']
include = '\\.py$'

[tool.isort]
line_length=120                # corresponds to -w  flag
multi_line_output=3            # corresponds to -m  flag
include_trailing_comma=true    # corresponds to -tc flag
skip_glob = '^((?!py$).)*$'    # this makes sort all Python files
known_third_party = ["cognite"]

[tool.poetry.dependencies]
python = ">=3.7,<3.11"

[tool.poetry.dev-dependencies]
pyinstaller = "^4.7"
macholib = {{version = "^1.14", platform = "darwin"}}             # Used by pyinstaller pn Mac OS
pywin32-ctypes = {{version = "^0.2.0", platform = "win32"}}       # Used by pyinstaller on Windows
pefile = "^2019.4.18"                                           # Used by pyinstaller on Windows

[tool.poetry.scripts]
{name} = "{name}.__main__:main"

[build-system]
requires = ["poetry>=0.12"]
build-backend = "poetry.masonry.api"
"""

pre_commit_template = """
repos:
-   repo: https://github.com/asottile/seed-isort-config
    rev: v2.2.0
    hooks:
    -   id: seed-isort-config
-   repo: https://github.com/pre-commit/mirrors-isort
    rev: v5.9.3
    hooks:
    -   id: isort
        additional_dependencies: [toml]
-   repo: https://github.com/psf/black
    rev: 21.9b0
    hooks:
      - id: black
-   repo: https://github.com/pre-commit/mirrors-mypy
    rev: v0.910-1
    hooks:
    -   id: mypy
        additional_dependencies:
            - types-PyYAML
            - types-requests
            - types-retry
"""

mypy_config_template = """
[mypy]
disallow_untyped_defs = true
ignore_missing_imports = true

[mypy-tests.*]
ignore_errors = True
"""

config_template = """
from dataclasses import dataclass

from cognite.extractorutils.configtools import BaseConfig, StateStoreConfig


@dataclass
class ExtractorConfig:
    state_store: StateStoreConfig = StateStoreConfig()


@dataclass
class Config(BaseConfig):
    extractor: ExtractorConfig = ExtractorConfig()
"""

configfile_template = """
logger:
    console:
        level: INFO

cognite:
    # Read these from environment variables
    host: ${COGNITE_BASE_URL}
    project: ${COGNITE_PROJECT}

    idp-authentication:
        token-url: ${COGNITE_TOKEN_URL}

        client-id: ${COGNITE_CLIENT_ID}
        secret: ${COGNITE_CLIENT_SECRET}
        scopes:
            - ${COGNITE_BASE_URL}/.default
"""

main_template = """
from cognite.extractorutils import Extractor

from {name} import __version__
from {name}.extractor import run_extractor
from {name}.config import Config


def main() -> None:
    with Extractor(
        name="{name}",
        description="{description}",
        config_class=Config,
        run_handle=run_extractor,
        version=__version__,
    ) as extractor:
        extractor.run()


if __name__ == "__main__":
    main()
"""

extractor_template = """
from threading import Event

from cognite.client import CogniteClient
from cognite.extractorutils.statestore import AbstractStateStore

from {name}.config import Config


def run_extractor(cognite: CogniteClient, states: AbstractStateStore, config: Config, stop_event: Event) -> None:
    print("Hello, world!")
"""


def initialize_project() -> None:
    name = prompt("extractor name").replace(" ", "_").replace("-", "_").lower()
    description = prompt("description")
    author = prompt("author", get_git_user())

    with open("pyproject.toml", "w") as pyproject_file:
        pyproject_file.write(pyproject_template.format(name=name, description=description, author=author))
    with open("mypy.ini", "w") as mypy_file:
        mypy_file.write(mypy_config_template)
    with open(".pre-commit-config.yaml", "w") as pre_commit_file:
        pre_commit_file.write(pre_commit_template)
    print("Fetching gitignore template from GitHub")
    gitignore_template = requests.get("https://raw.githubusercontent.com/github/gitignore/master/Python.gitignore").text
    with open(".gitignore", "w") as gitignore_file:
        gitignore_file.write(gitignore_template)
    with open("example_config.yaml", "w") as configfile_file:
        configfile_file.write(configfile_template)

    if not os.path.isdir(".git"):
        os.system("git init")

    os.mkdir(name)
    with open(os.path.join(name, "__init__.py"), "w") as init_file:
        init_file.write('__version__ = "1.0.0"')
    with open(os.path.join(name, "__main__.py"), "w") as main_file:
        main_file.write(main_template.format(name=name, description=description))
    with open(os.path.join(name, "config.py"), "w") as config_file:
        config_file.write(config_template)
    with open(os.path.join(name, "extractor.py"), "w") as extractor_file:
        extractor_file.write(extractor_template.format(name=name))

    os.system("poetry run pip install --upgrade pip")
    os.system("poetry add cognite-sdk-core cognite-extractor-utils")
    os.system("poetry add -D mypy flake8 black isort pre-commit")
    os.system("poetry lock")
    os.system("poetry install")
    os.system("poetry run pre-commit autoupdate")
    os.system("poetry run pre-commit install")
    os.system(f"poetry run black {name}")
    os.system(f"poetry run isort {name}")
