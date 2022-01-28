# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pontos',
 'pontos.changelog',
 'pontos.git',
 'pontos.github',
 'pontos.github.actions',
 'pontos.release',
 'pontos.terminal',
 'pontos.updateheader',
 'pontos.updateheader.templates.AGPL-3.0-or-later',
 'pontos.updateheader.templates.GPL-2.0-or-later',
 'pontos.updateheader.templates.GPL-3.0-or-later',
 'pontos.version',
 'tests',
 'tests.changelog',
 'tests.git',
 'tests.github',
 'tests.github.actions',
 'tests.release',
 'tests.terminal',
 'tests.updateheader',
 'tests.version']

package_data = \
{'': ['*'], 'pontos.updateheader': ['templates/GPL-2.0-only/*']}

modules = \
['poetry']
install_requires = \
['colorful>=0.5.4,<0.6.0',
 'packaging>=20.3,<21.0',
 'requests>=2.24.0,<3.0.0',
 'tomlkit>=0.5.11']

entry_points = \
{'console_scripts': ['pontos = pontos:main',
                     'pontos-changelog = pontos.changelog:main',
                     'pontos-github = pontos.github:main',
                     'pontos-release = pontos.release:main',
                     'pontos-update-header = pontos.updateheader:main',
                     'pontos-version = pontos.version:main']}

setup_kwargs = {
    'name': 'pontos',
    'version': '22.1.3',
    'description': 'Common utilities and tools maintained by Greenbone Networks',
    'long_description': '![Greenbone Logo](https://www.greenbone.net/wp-content/uploads/gb_logo_resilience_horizontal.png)\n\n# Pontos - Greenbone Python Utilities and Tools <!-- omit in toc -->\n\n[![GitHub releases](https://img.shields.io/github/release/greenbone/pontos.svg)](https://github.com/greenbone/pontos/releases)\n[![PyPI release](https://img.shields.io/pypi/v/pontos.svg)](https://pypi.org/project/pontos/)\n[![code test coverage](https://codecov.io/gh/greenbone/pontos/branch/master/graph/badge.svg)](https://codecov.io/gh/greenbone/pontos)\n[![Build and test](https://github.com/greenbone/pontos/actions/workflows/ci-python.yml/badge.svg)](https://github.com/greenbone/pontos/actions/workflows/ci-python.yml)\n\nThe **pontos** Python package is a collection of utilities, tools, classes and\nfunctions maintained by [Greenbone Networks].\n\nPontos is the German name of the Greek titan [Pontus](https://en.wikipedia.org/wiki/Pontus_(mythology)),\nthe titan of the sea.\n\n## Table of Contents <!-- omit in toc -->\n\n- [Tools](#tools)\n- [Installation](#installation)\n  - [Requirements](#requirements)\n  - [Install using pip](#install-using-pip)\n  - [Install using poetry](#install-using-poetry)\n- [Development](#development)\n- [Maintainer](#maintainer)\n- [Contributing](#contributing)\n- [License](#license)\n\n## Tools and Utilities\n\n`pontos` comes with a continiously increasing set of features.\nThe following commands are currently available:\n\n* `pontos-release` - Release handling utility for C and Python Projects\n>We also provide easy-to-use [GitHub Actions](https://github.com/greenbone/actions/#usage), that we recommended to use instead of manually releasing with pontos-release.\n```bash\n# Prepare the next patch release (x.x.2) of project <foo>, use conventional commits for release notes\npontos-release prepare --project <foo> -patch -CC\n# Release that patch version of project <foo>\npontos-release release --project <foo>\n# Sign a release:\npontos-release sign --project <foo> --release-version 1.2.3 --signing-key 1234567890ABCDEFEDCBA0987654321 [--passphrase <for_that_key>]\n```\n* `pontos-version` - Version handling utility for C, Go and Python Projects\n```bash\n# Update version of this project to 22.1.1\npontos-version update 22.1.1\n# Show current projects version\npontos-version show\n```\n* `pontos-update-header` - Handling Copyright header for various file types and licences\n>We also provide an easy-to-use [GitHub Action](https://github.com/greenbone/actions/#usage), that updates copyright year in header of files and creates a Pull Request.\n```bash\n# Update year in Copyright header in files, also add missing headers\npontos-update-header -d <dir1> <dir2>\n```\n* `pontos-changelog` - Parse conventional commits in the current branch, creating CHANGELOG.md file\n```bash\n# Parse conventional commits and create <changelog_file>\npontos-changelog -o <changelog-file>\n```\n* pontos-github` - Handling GitHub operations, like Pull Requests (beta)\n```bash\n# create a PR on GitHub\npontos-github pr <orga/repo> <head> <target> <pr_title> [--body <pr_body>]\n```\n\n* pontos` also comes with a Terminal interface printing prettier outputs\n```python\nimport pontos.terminal.terminal\n\nterm = terminal.Terminal()\nwith term.indent():\n    term.ok("Hello indented World")\n```\n* `pontos` also comes with git and GitHub APIs\n```python\nimport pontos.git\nimport pontos.github\n```\n\n## Installation\n\n### Requirements\n\nPython 3.7 and later is supported.\n\n### Install using pip\n\npip 19.0 or later is required.\n\n> **Note**: All commands listed here use the general tool names. If some of\n> these tools are provided by your distribution, you may need to explicitly use\n> the Python 3 version of the tool, e.g. **`pip3`**.\n\nYou can install the latest stable release of **pontos** from the Python\nPackage Index (pypi) using [pip]\n\n    pip install --user pontos\n\n### Install using poetry\n\nBecause **pontos** is a Python library you most likely need a tool to\nhandle Python package dependencies and Python environments. Therefore we\nstrongly recommend using [pipenv] or [poetry].\n\nYou can install the latest stable release of **pontos** and add it as\na dependency for your current project using [poetry]\n\n    poetry add pontos\n\nFor installation via pipenv please take a look at their [documentation][pipenv].\n\n## Development\n\n**pontos** uses [poetry] for its own dependency management and build\nprocess.\n\nFirst install poetry via pip\n\n    pip install --user poetry\n\nAfterwards run\n\n    poetry install\n\nin the checkout directory of **pontos** (the directory containing the\n`pyproject.toml` file) to install all dependencies including the packages only\nrequired for development.\n\nAfterwards activate the git hooks for auto-formatting and linting via\n[autohooks].\n\n    poetry run autohooks activate\n\nValidate the activated git hooks by running\n\n    poetry run autohooks check\n\n## Maintainer\n\nThis project is maintained by [Greenbone Networks GmbH][Greenbone Networks]\n\n## Contributing\n\nYour contributions are highly appreciated. Please\n[create a pull request](https://github.com/greenbone/pontos/pulls)\non GitHub. Bigger changes need to be discussed with the development team via the\n[issues section at GitHub](https://github.com/greenbone/pontos/issues)\nfirst.\n\n## License\n\nCopyright (C) 2020-2021 [Greenbone Networks GmbH][Greenbone Networks]\n\nLicensed under the [GNU General Public License v3.0 or later](LICENSE).\n\n[Greenbone Networks]: https://www.greenbone.net/\n[poetry]: https://python-poetry.org/\n[pip]: https://pip.pypa.io/\n[pipenv]: https://pipenv.pypa.io/\n[autohooks]: https://github.com/greenbone/autohooks\n',
    'author': 'Greenbone Networks GmbH',
    'author_email': 'info@greenbone.net',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'py_modules': modules,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
