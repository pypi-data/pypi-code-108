# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': '.'}

packages = \
['cognite',
 'cognite.transformations_cli',
 'cognite.transformations_cli.commands',
 'cognite.transformations_cli.commands.deploy']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.0.1,<9.0.0',
 'cognite-extractor-utils>=1.6.2,<2.0.0',
 'cognite-sdk>=2.38.1,<3.0.0',
 'regex>=2021.11.10,<2022.0.0',
 'sqlparse>=0.4.2,<0.5.0',
 'tabulate>=0.8.9,<0.9.0',
 'types-retry>=0.1.5,<0.2.0',
 'types-tabulate>=0.8.3,<0.9.0']

entry_points = \
{'console_scripts': ['transformations-cli = '
                     'cognite.transformations_cli.__main__:main']}

setup_kwargs = {
    'name': 'cognite-transformations-cli',
    'version': '1.3.0',
    'description': 'A CLI for the Transformations service in CDF',
    'long_description': "# Cognite Transformations CLI\n\n[![Build Status](https://github.com/cognitedata/transformations-cli/workflows/release/badge.svg)](https://github.com/cognitedata/transformations-cli/actions)\n[![Documentation Status](https://readthedocs.com/projects/cognite-transformations-cli/badge/?version=latest)](https://cognite-transformations-cli.readthedocs-hosted.com/en/latest/?badge=latest)\n[![codecov](https://codecov.io/gh/cognitedata/transformations-cli/branch/main/graph/badge.svg?token=PSkli74vvX)](https://codecov.io/gh/cognitedata/transformations-cli)\n[![PyPI version](https://badge.fury.io/py/cognite-transformations-cli.svg)](https://pypi.org/project/cognite-transformations-cli)\n![PyPI - Python Version](https://img.shields.io/pypi/pyversions/cognite-transformations-cli)\n[![License](https://img.shields.io/github/license/cognitedata/python-extractor-utils)](LICENSE)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)\n\n## Transformations CLI\n\nUse the Transformations command-line interface (**Transformations CLI**) to manage the lifecycle of your transformation jobs using the command line. With the Transformations CLI, you can process data from the CDF staging area (RAW) into the CDF data model. To learn more about how the Cognite Transformations CLI package works, see the **documentation** [here](https://cognite-transformations-cli.readthedocs-hosted.com/en/latest/)\n\nThe **Transformations CLI** is based on Python and replaces the [Jetfire CLI](https://github.com/cognitedata/jetfire-cli).\n\n### GitHub Action\n\nThe **Transformations CLI** provides a GitHub Action to deploy transformations. You'll find the documentation [here](githubaction.md).\n\nWe've also created a **CI/CD template** that uses GitHub Workflows. You'll find the documentation [here](https://github.com/cognitedata/transformations-action-template).\n\n### Migrating from Jetfire CLI\n\n**Transformations CLI** replaces the [Jetfire CLI](https://github.com/cognitedata/jetfire-cli). If you've already used the **Jetfire CLI** in a GitHub Action, we recommend migrating to the **Transformations CLI** GitHub Action. You'll find the migration guide [here](migrationguide.md).\n\n### Contributing\n\nWe use [poetry](https://python-poetry.org) to manage dependencies and to administrate virtual environments. To develop\n**Transformations CLI**, follow these steps to set up your local environment:\n\n1.  Install poetry: (add `--user` if desirable)\n    ```\n    $ pip install poetry\n    ```\n2.  Clone repository:\n    ```\n    $ git clone git@github.com:cognitedata/transformations-cli.git\n    ```\n3.  Move into the newly created local repository:\n    ```\n    $ cd transformations-cli\n    ```\n4.  Create a virtual environment and install dependencies:\n\n    ```\n    $ poetry install\n    ```\n\n5.  All the code must pass [black](https://github.com/ambv/black) and [isort](https://github.com/timothycrosley/isort) style\n    checks before it can be merged. We recommend installing pre-commit hooks to ensure this locally before you commit your code:\n\n```\n$ poetry run pre-commit install\n```\n\n6. To publish a new version, change the version in `cognite/transformations_cli/__init__.py` and `pyproject.toml`. Make sure to update the `CHANGELOG`.\n\nThis project adheres to the [Contributor Covenant v2.0](https://www.contributor-covenant.org/version/2/0/code_of_conduct/)\nas a code of conduct.\n",
    'author': 'Mathias Lohne',
    'author_email': 'mathias.lohne@cognite.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/cognitedata/transformations-cli',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
