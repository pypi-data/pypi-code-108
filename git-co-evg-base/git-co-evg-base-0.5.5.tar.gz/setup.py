# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['goodbase', 'goodbase.models', 'goodbase.services']

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
 'structlog>=21.1.0,<22.0.0',
 'xdg>=5.1.1,<6.0.0']

entry_points = \
{'console_scripts': ['git-co-evg-base = goodbase.goodbase_cli:main']}

setup_kwargs = {
    'name': 'git-co-evg-base',
    'version': '0.5.5',
    'description': 'Find a good commit to base your work on',
    'long_description': "# git-co-evg-base\n\nFind and checkout a recent git commit that matches the specified criteria.\n\n![PyPI - Python Version](https://img.shields.io/pypi/pyversions/git-co-evg-base) [![PyPI](https://img.shields.io/pypi/v/git-co-evg-base.svg)](https://pypi.org/project/git-co-evg-base/) [![Upload Python Package](https://github.com/dbradf/git-co-evg-base/actions/workflows/deploy.yml/badge.svg)](https://github.com/dbradf/git-co-evg-base/actions/workflows/deploy.yml) [![test-python-project](https://github.com/dbradf/git-co-evg-base/actions/workflows/test.yml/badge.svg)](https://github.com/dbradf/git-co-evg-base/actions/workflows/test.yml)\n\n## Table of contents\n\n1. [Description](#description)\n2. [Dependencies](#dependencies)\n3. [Installation](#installation)\n4. [Usage](#usage)\n5. [Contributor's Guide](#contributors-guide)\n    - [Setting up a local development environment](#setting-up-a-local-development-environment)\n    - [linting/formatting](#lintingformatting)\n    - [Running tests](#running-tests)\n    - [Automatically running checks on commit](#automatically-running-checks-on-commit)\n    - [Versioning](#versioning)\n    - [Code Review](#code-review)\n    - [Deployment](#deployment)\n6. [Resources](#resources)\n\n## Description\n\nWhen running an Evergreen patch build, it can be useful that base your\nchanges on a commit in which the tests in Evergreen have already been run.\nThis way if you encounter any failures in your patch build, you can easily\ncompare the failure with what was seen in the base commit to understand if\nyour changes may have introduced the failure.\n\nThis command allows you to specify criteria to use to find and checkout a\ngit commit to start work from.\n\n## Dependencies\n\n* Python 3.8 or later\n* git\n* [Evergreen config file](https://github.com/evergreen-ci/evergreen/wiki/Using-the-Command-Line-Tool#downloading-the-command-line-tool)\n\n## Installation\n\nWe strongly recommend using a tool like [pipx](https://pypa.github.io/pipx/) to install\nthis tool. This will isolate the dependencies and ensure they don't conflict with other tools.\n\n```bash\n$ pipx install git-co-evg-base\n```\n\n## Usage\n\nDetailed usage documentation can be found [here](https://github.com/dbradf/git-co-evg-base/tree/master/docs/usage.md).\n\n```\nUsage: git-co-evg-base [OPTIONS]\n\n  Find and checkout a recent git commit that matches the specified criteria.\n\n  When running an Evergreen patch build, it can be useful that base your changes on a commit in\n  which the tests in Evergreen have already been run. This way if you encounter any failures in\n  your patch build, you can easily compare the failure with what was seen in the base commit to\n  understand if your changes may have introduced the failure.\n\n  This command allows you to specify criteria to use to find and checkout a git commit to start\n  work from.\n\nCriteria:\n\n  There are 4 criteria that can be specified:\n\n  * The percentage of tasks that have passed in each build.\n\n  * The percentage of tasks that have run in each build.\n\n  * Specific tasks that must have passed in each build (if they are part of that build).\n\n  * Specific tasks that must have run in each build (if they are part of that build).\n\n  If not criteria are specified, a success threshold of 0.95 will be used.\n\n  Additionally, you can specify which build variants the criteria should be checked against. By\n  default, only builds that end in 'required' will be checked.\n\nNotes:\n\n  If you have any evergreen modules with local checkouts in the location specified in your\n  project's evergreen.yml configuration file. They will automatically be checked out to the\n  revision that was run in Evergreen with the revision of the base project.\n\nExamples:\n\n  Working on a fix for a task 'replica_sets' on the build variants 'enterprise-rhel-80-64-bit' and\n  'enterprise-windows', to ensure the task has been run on those build variants:\n\n      git co-evg-base --run-task replica_sets --build-variant enterprise-rhel-80-64-bit --build-variant --enterprise-windows\n\n  Starting a new change, to ensure that there are no systemic failures on the base commit:\n\n      git co-evg-base --pass-threshold 0.98\n      \nOptions:\n  --passing-task TEXT             Specify a task that needs to be passing (can be specified\n                                  multiple times).\n  --run-task TEXT                 Specify a task that needs to be run (can be specified multiple\n                                  times).\n  --run-threshold FLOAT           Specify the percentage of tasks that need to be run.\n  --pass-threshold FLOAT          Specify the percentage of tasks that need to be successful.\n  --evg-config-file PATH          File containing evergreen authentication information.\n  --evg-project TEXT              Evergreen project to query against.\n  --build-variant TEXT            Regex of Build variants to check (can be specified multiple\n                                  times).\n  --commit-lookback INTEGER       Number of commits to check before giving up\n  --timeout-secs INTEGER          Number of seconds to search for before giving up.\n  --commit-limit TEXT             Oldest commit to check before giving up.\n  --git-operation [checkout|rebase|merge|none]\n                                  Git operations to perform with found commit [default=checkout].\n  -b, --branch TEXT               Name of branch to create on checkout.\n  --save-criteria TEXT            Save the specified criteria rules under the specified name for\n                                  future use.\n  --use-criteria TEXT             Use previously save criteria rules.\n  --list-criteria                 Display saved criteria.\n  --override                      Override saved conflicting save criteria rules.\n  --export-criteria TEXT          Specify saved criteria to export to a file.\n  --export-file PATH              File to write exported rules to.\n  --import-criteria PATH          Import previously exported criteria.\n  --output-format [plaintext|yaml|json]\n                                  Format of the command output [default=plaintext].\n  --verbose                       Enable debug logging.\n  --help                          Show this message and exit.\n```\n\nCheckout using the default criteria:\n\n```bash\n$ git co-evg-base\n```\n\nCheckout with successful tasks 'auth' and 'auth_audit' on builds 'enterprise-windows' and \n'enterprise-rhel-80-64-bit' and 95% of the tasks are passing.\n\n```bash\n$ git co-evg-base --passing-task auth --passing-task auth_audit --run-threshold 0.95 --build-variant enterprise-windows --build-variant enterprise-rhel-80-64-bit\n```\n\n## Contributor's Guide\n\n### Setting up a local development environment\n\nThis project uses [poetry](https://python-poetry.org/) for setting up a local environment.\n\n```bash\ngit clone ...\ncd ...\npoetry install\n```\n\n### linting/formatting\n\nThis project uses [black](https://black.readthedocs.io/en/stable/) and \n[isort](https://pycqa.github.io/isort/) for formatting.\n\n```bash\npoetry run black src tests\npoetry run isort src tests\n```\n\n### Running tests\n\nThis project uses [pytest](https://docs.pytest.org/en/6.2.x/) for testing.\n\n```bash\npoetry run pytest\n```\n\n### Automatically running checks on commit\n\nThis project has [pre-commit](https://pre-commit.com/) configured. Pre-commit will run \nconfigured checks at git commit time. To enable pre-commit on your local repository run:\n\n```bash\npoetry run pre-commit install\n```\n\n### Versioning\n\nThis project uses [semver](https://semver.org/) for versioning.\n\nPlease include a description what is added for each new version in `CHANGELOG.md`.\n\n### Code Review\n\nPlease open a Github Pull Request for code review.\n\n### Deployment\n\nDeployment to pypi is automatically triggered on merges to master.\n\n## Resources\n\n* [Evergreen REST documentation](https://github.com/evergreen-ci/evergreen/wiki/REST-V2-Usage)\n",
    'author': 'David Bradford',
    'author_email': 'david.bradford@mongodb.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/dbradf/git-co-evg-base',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
