# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['convbump']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.0.3,<9.0.0', 'semver>=2.13.0,<3.0.0']

entry_points = \
{'console_scripts': ['convbump = convbump.__main__:convbump']}

setup_kwargs = {
    'name': 'convbump',
    'version': '0.3.1',
    'description': 'Tool for Conventional Commits',
    'long_description': 'Convbump\n=====\n[![Python versions](https://img.shields.io/pypi/pyversions/convbump)](https://pypi.org/project/convbump/)\n[![Latest Version](https://img.shields.io/pypi/v/convbump.svg)](https://pypi.org/project/convbump/)\n[![BSD License](https://img.shields.io/pypi/l/convbump.svg)](https://github.com/playpauseandstop/convbump/blob/master/LICENSE)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n\n`convbump` is a simple tool to work with conventional commits.\n\nUse the `version` command to find the next version in your repository\nbased on the conventional commits.\n\nUse the `changelog` command to generate a nicely formatted changelog\n(Github markdown compatible).\n\n## Development\nThe application is written in Python and uses\n[Poetry](https://python-poetry.org/docs/) to configure the package and manage\nits dependencies.\n\nMake sure you have [Poetry CLI installed](https://python-poetry.org/docs/#installation).\nThen you can run\n\n    $ poetry install\n\nwhich will install the project dependencies (including `dev` dependencies) into a\nPython virtual environment managed by Poetry (alternatively, you can activate\nyour own virtual environment beforehand and Poetry will use that).\n\n### Run tests with pytest\n\n    $ poetry run pytest\n\nor\n\n\t$ poetry shell\n\t$ pytest\n\n`pytest` will take configuration from `pytest.ini` file first (if present), then\nfrom `pyproject.toml`. Add any local configuration to `pytest.ini`.\nConfiguration in `pyproject.toml` will be used in CI. You can run your\ntests the same way as CI to catch any errors\n\n\t$ pytest -c pyproject.toml\n\n### Code formatting\nThe application is formatted using [black](https://black.readthedocs.io/en/stable/) and [isort](https://pycqa.github.io/isort/).  \nYou can either run black and isort manually or use prepared [Poe](https://github.com/nat-n/poethepoet) task to format the whole project.\n\n\t$ poetry run poe format-code\nor\n\n\t$ poetry shell\n\t$ poe format-code\n',
    'author': 'Max Kovykov',
    'author_email': 'maxim.kovykov@avast.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
