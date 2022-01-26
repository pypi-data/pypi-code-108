# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['emm', 'emm.services']

package_data = \
{'': ['*']}

install_requires = \
['Inject>=4.3.1,<5.0.0',
 'PyYAML>=5.4.1,<6.0.0',
 'click>=8,<9',
 'evergreen.py>=3.2.7,<4.0.0',
 'plumbum>=1.7.0,<2.0.0',
 'pydantic>=1.8.2,<2.0.0',
 'rich>=10.9.0,<11.0.0',
 'shrub.py>=3.0.0,<4.0.0',
 'structlog>=21.1.0,<22.0.0',
 'xdg>=5.1.1,<6.0.0']

entry_points = \
{'console_scripts': ['evg-module-manager = emm.emm_cli:cli']}

setup_kwargs = {
    'name': 'evg-module-manager',
    'version': '0.1.9',
    'description': 'Manage Evergreen modules locally.',
    'long_description': "# Evergreen Module Manager\n\nManage Evergreen modules in your local environment.\n\n![PyPI - Python Version](https://img.shields.io/pypi/pyversions/evg-module-manager) [![PyPI](https://img.shields.io/pypi/v/evg-module-manager.svg)](https://pypi.org/project/evg-module-manager/)\n\n## Table of contents\n\n1. [Description](#description)\n2. [Dependencies](#dependencies)\n3. [Installation](#installation)\n4. [Usage](#usage)\n5. [Contributor's Guide](#contributors-guide)\n    - [Setting up a local development environment](#setting-up-a-local-development-environment)\n    - [linting/formatting](#lintingformatting)\n    - [Running tests](#running-tests)\n    - [Automatically running checks on commit](#automatically-running-checks-on-commit)\n    - [Versioning](#versioning)\n    - [Code Review](#code-review)\n    - [Deployment](#deployment)\n6. [Resources](#resources)\n\n## Description\n\nThe evg-module-manager is a tool to help improve the local workflows of working with modules in\nyour evergreen projects. It will help you keep any modules defined in your local project in sync.\nIt supports the following functionality:\n\n* List what modules are defined in the local project.\n* List what modules are currently active in your local repo.\n* Clone a module repository.\n* Enable/disable modules in your local repo.\n* Create an evergreen patch build that includes changes from the local patch build and all enabled\n  modules.\n* Submit a changes to the commit-queue that includes changes from the local patch build and all\n  enabled modules.\n\n## Dependencies\n\n* Python 3.8 or later\n* git\n* evergreen command line tool\n* [Evergreen config file](https://github.com/evergreen-ci/evergreen/wiki/Using-the-Command-Line-Tool#downloading-the-command-line-tool)\n* [github CLI](https://cli.github.com/)\n\n## Installation\n\nWe strongly recommend using a tool like [pipx](https://pypa.github.io/pipx/) to install\nthis tool. This will isolate the dependencies and ensure they don't conflict with other tools.\n\n```bash\n$ pipx install evg-module-manager\n```\n\n## Usage\n\nSee the [usage](docs/usage.md) documentation for details about using this tool.\n\n```bash\nevg-module-manager --help\nUsage: evg-module-manager [OPTIONS] COMMAND [ARGS]...\n\n  Evergreen Module Manager is a tool help simplify the local workflows of evergreen modules.\n\nOptions:\n  --modules-dir PATH      Directory to store module repositories [default='..']\n  --evg-config-file PATH  Path to file with evergreen auth configuration\n                          [default='/Users/user/.evergreen.yml']\n  --evg-project TEXT      Name of Evergreen project [default='mongodb-mongo-master']\n  --help                  Show this message and exit.\n\nCommands:\n  commit-queue  Submit changes from the base repository and any enabled modules to the...\n  create-branch Perform git checkout operation to create the branch.\n  disable       Disable the specified module in the current repo.\n  enable        Enable the specified module in the current repo.\n  git-commit    Perform git commit of changes in each module.\n  list-modules  List the modules available for the current repo.\n  patch         Create an Evergreen patch with changes from the base repo and any enabled...\n  pull-request   Create pull request for the changes in each module.\n  update-branch Perform git merge|rebase operation to update the branch.\n```\n\n## Contributor's Guide\n\n### Setting up a local development environment\n\nThis project uses [poetry](https://python-poetry.org/) for setting up a local environment.\n\n```bash\ngit clone ...\ncd evg-module-manager\npoetry install\n```\n\n### linting/formatting\n\nThis project uses [black](https://black.readthedocs.io/en/stable/) and\n[isort](https://pycqa.github.io/isort/) for formatting.\n\n```bash\npoetry run black src tests\npoetry run isort src tests\n```\n\n### Running tests\n\nThis project uses [pytest](https://docs.pytest.org/en/6.2.x/) for testing.\n\n```bash\npoetry run pytest\n```\n\n### Automatically running checks on commit\n\nThis project has [pre-commit](https://pre-commit.com/) configured. Pre-commit will run\nconfigured checks at git commit time. To enable pre-commit on your local repository run:\n\n```bash\npoetry run pre-commit install\n```\n\n### Versioning\n\nThis project uses [semver](https://semver.org/) for versioning.\n\nPlease include a description what is added for each new version in `CHANGELOG.md`.\n\n### Code Review\n\nPlease open a Github Pull Request for code review.\n\n### Deployment\n\nDeployment to pypi is automatically triggered on merges to main.\n\n## Resources\n\n* [Evergreen REST documentation](https://github.com/evergreen-ci/evergreen/wiki/REST-V2-Usage)\n",
    'author': 'Dev Prod DAG',
    'author_email': 'dev-prod-dag@mongodb.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/evergreen-ci/evg-module-manager',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
