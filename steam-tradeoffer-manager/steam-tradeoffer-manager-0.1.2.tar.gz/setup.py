# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['steam_tradeoffer_manager', 'steam_tradeoffer_manager.base']

package_data = \
{'': ['*']}

install_requires = \
['steamio>=0.8.6,<0.9.0']

setup_kwargs = {
    'name': 'steam-tradeoffer-manager',
    'version': '0.1.2',
    'description': 'Small package that help managing steam trade offers and steam bots',
    'long_description': '# Python-steam-tradeoffer-manager\n\n[![license](https://img.shields.io/github/license/somespecialone/python-steam-tradeoffer-manager)](https://github.com/somespecialone/python-steam-tradeoffer-manager/blob/master/LICENSE)\n[![pypi](https://img.shields.io/pypi/v/steam-tradeoffer-manager)](https://pypi.org/project/steam-tradeoffer-manager)\n[![Docs](https://github.com/somespecialone/python-steam-tradeoffer-manager/actions/workflows/docs.yml/badge.svg)](https://github.com/somespecialone/python-steam-tradeoffer-manager/actions/workflows/docs.yml)\n[![Tests](https://github.com/somespecialone/python-steam-tradeoffer-manager/actions/workflows/tests.yml/badge.svg)](https://github.com/somespecialone/python-steam-tradeoffer-manager/actions/workflows/tests.yml)\n[![codecov](https://codecov.io/gh/somespecialone/python-steam-tradeoffer-manager/branch/master/graph/badge.svg?token=H3JL81SL7P)](https://codecov.io/gh/somespecialone/python-steam-tradeoffer-manager)\n[![CodeFactor](https://www.codefactor.io/repository/github/somespecialone/python-steam-tradeoffer-manager/badge)](https://www.codefactor.io/repository/github/somespecialone/python-steam-tradeoffer-manager)\n[![versions](https://img.shields.io/pypi/pyversions/steam-tradeoffer-manager)](https://pypi.org/project/steam-tradeoffer-manager)\n[![black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![steam](https://shields.io/badge/steam-1b2838?logo=steam)](https://store.steampowered.com/)\n\n## Installation\n\n```bash\n# using pip\n$ pip install steam-tradeoffer-manager\n\n# using pipenv\n$ pipenv install steam-tradeoffer-manager\n\n# using poetry\n$ poetry add steam-tradeoffer-manager\n```\n\nIf you want to have the latest updates not included in release and published:\n```sh\n$ pip install git+https://github.com/somespecialone/python-steam-tradeoffer-manager.git@master\n\n$ pipenv install git+https://github.com/somespecialone/python-steam-tradeoffer-manager.git@master\n\n$ poetry add git+https://github.com/somespecialone/python-steam-tradeoffer-manager#master\n```\n\n***Coming soon...***\n',
    'author': 'somespecialone',
    'author_email': 'tkachenkodmitriy@yahoo.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/somespecialone/python-steam-tradeoffer-manager/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
