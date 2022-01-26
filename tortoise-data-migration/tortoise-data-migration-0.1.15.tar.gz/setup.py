# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tortoise_data_migration']

package_data = \
{'': ['*']}

install_requires = \
['tortoise-orm>=0.17.5,<0.19']

setup_kwargs = {
    'name': 'tortoise-data-migration',
    'version': '0.1.15',
    'description': 'Tortoise migrations for data, not structure',
    'long_description': '# tortoise-data-migration\n\n[![tests](https://github.com/Ekumen-OS/tortoise-data-migration/actions/workflows/tests.yaml/badge.svg)](https://github.com/Ekumen-OS/tortoise-data-migration/actions/workflows/tests.yaml)\n[![codecov](https://codecov.io/gh/Ekumen-OS/tortoise-data-migration/branch/main/graph/badge.svg?token=P92AYYHAR1)](https://codecov.io/gh/Ekumen-OS/tortoise-data-migration)\n[![black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![poetry-managed](https://img.shields.io/badge/poetry-managed-blueviolet)](https://python-poetry.org)\n![PyPI - Python Version](https://img.shields.io/pypi/pyversions/tortoise-data-migration)\n![PyPI - Wheel](https://img.shields.io/pypi/wheel/tortoise-data-migration)\n[![PyPI](https://img.shields.io/pypi/v/tortoise-data-migration?logo=python)](https://pypi.org/project/tortoise-data-migration/)\n[![Total alerts](https://img.shields.io/lgtm/alerts/g/Ekumen-OS/tortoise-data-migration.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/Ekumen-OS/tortoise-data-migration/alerts/)\n[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/Ekumen-OS/tortoise-data-migration.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/Ekumen-OS/tortoise-data-migration/context:python)\n\n\n`tortoise-data-migration` is a very simple project meant to perform migrations of data, similar to regular structural migrations.\n\nThe main use case is when your system has some "default data" that needs to exist for the system to work. Some examples:\n - The default username/password of a system\n - The default configuration values (if you store the config in the DB)\n\nThese values could be set in the system as part of the installation process, but then when writing tests that use those,\nyou would have to somehow get those values to the DB. So you create a test fixture, and very probably you will be\nintroducing duplication (the bringup/installation process has these values, and the fixture too).\n\ntortoise-data-migrations are meant to be executed by the software (either during test execution of production) after the\ndatabase structure is up-to-date (in production software after running [aerich](https://github.com/tortoise/aerich) migrations for example\nor during tests after the DB setup is done), but before the actual software starts executing. That\'s why\n`tortoise-data-migration` is a library and not a command line tool.\n\n\n## Installation\n\n### Pip\n\n`pip install tortoise-data-migration`\n\n### Pipenv\n\n`pipenv install tortoise-data-migration`\n\n### Poetry\n\n`poetry add tortoise-data-migration`\n\n### PDM\n\n`pdm add tortoise-data-migration`\n\n## Notes for maintainers\n\n### Release\n\nTo create a new release, create a github release and a github action will take care of building and publishing. After\nthat, there will be a PR automatically created to bump the version in `main`.\n',
    'author': 'Guillermo Manzato',
    'author_email': 'manzato@ekumenlabs.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Ekumen-OS/tortoise-data-migration',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
