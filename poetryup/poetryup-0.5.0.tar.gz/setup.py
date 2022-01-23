# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['poetryup']

package_data = \
{'': ['*']}

install_requires = \
['packaging>=21.3,<22.0', 'tomlkit>=0.8.0,<0.9.0', 'typer>=0.4.0,<0.5.0']

entry_points = \
{'console_scripts': ['poetryup = poetryup.main:app']}

setup_kwargs = {
    'name': 'poetryup',
    'version': '0.5.0',
    'description': 'Update dependencies and bump their version in the pyproject.toml file',
    'long_description': "# PoetryUp\n\n![build](https://github.com/MousaZeidBaker/poetryup/workflows/Publish/badge.svg)\n![test](https://github.com/MousaZeidBaker/poetryup/workflows/Test/badge.svg)\n[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)\n![python_version](https://img.shields.io/badge/python-%3E=3.6-blue.svg)\n[![pypi_v](https://img.shields.io/pypi/v/poetryup.svg)](https://pypi.org/project/poetryup)\n[![pypi_dm](https://img.shields.io/pypi/dm/poetryup.svg)](https://pypi.org/project/poetryup)\n\nPoetryUp updates dependencies and bumps their version in the `pyproject.toml`\nfile with respect to their version constraint. The `poetry.lock` file will be\nrecreated as well. PoetryUp runs\n[poetry](https://github.com/python-poetry/poetry) commands, thus it's required\nto be installed. The difference between running `poetry update` and `poetryup`,\nis that the latter also modifies the `pyproject.toml` file.\n\n![poetryup_demo](https://raw.githubusercontent.com/MousaZeidBaker/poetryup/master/media/poetryup_demo.gif)\n\n## Usage\n```shell\npoetryup --help\n```\n\n## Automate Dependency Updates with GitHub Actions\nUse PoetryUp with GitHub actions to automate the process of updating\ndependencies, for reference see this project's [workflow\nconfiguration](https://github.com/MousaZeidBaker/poetryup/blob/master/.github/workflows/update-dependencies.yaml).\n\n## Contributing\nContributions are welcome via pull requests.\n\n## Issues\nIf you encounter any problems, please file an\n[issue](https://github.com/MousaZeidBaker/poetryup/issues) along with a detailed\ndescription.\n\n## Develop\nActivate virtual environment\n```shell\npoetry shell\n```\n\nInstall dependencies\n```shell\npoetry install --remove-untracked\n```\n\nInstall git hooks\n```shell\npre-commit install --hook-type pre-commit\n```\n\nRun tests\n```shell\npytest tests\n```\n\nRun linter\n```shell\nflake8 .\n```\n\nFormat code\n```shell\nblack .\n```\n\nSort imports\n```shell\nisort .\n```\n\nInstall current project from branch\n```shell\npoetry add git+https://github.com/MousaZeidBaker/poetryup.git#branch-name\n```\n",
    'author': 'Mousa Zeid Baker',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/MousaZeidBaker/poetryup',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
