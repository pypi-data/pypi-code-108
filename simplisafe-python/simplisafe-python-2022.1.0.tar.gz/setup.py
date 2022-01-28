# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['simplipy',
 'simplipy.device',
 'simplipy.device.sensor',
 'simplipy.system',
 'simplipy.util']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.8.0',
 'backoff>=1.11.1,<2.0.0',
 'docutils<0.18',
 'pytz>=2019.3,<2022.0',
 'voluptuous>=0.11.7,<0.13.0',
 'websockets>=8.1,<11.0']

setup_kwargs = {
    'name': 'simplisafe-python',
    'version': '2022.1.0',
    'description': 'A Python3, async interface to the SimpliSafe API',
    'long_description': '# 🚨 simplisafe-python: A Python3, async interface to the SimpliSafe™ API\n\n[![CI](https://github.com/bachya/simplisafe-python/workflows/CI/badge.svg)](https://github.com/bachya/simplisafe-python/actions)\n[![PyPi](https://img.shields.io/pypi/v/simplisafe-python.svg)](https://pypi.python.org/pypi/simplisafe-python)\n[![Version](https://img.shields.io/pypi/pyversions/simplisafe-python.svg)](https://pypi.python.org/pypi/simplisafe-python)\n[![License](https://img.shields.io/pypi/l/simplisafe-python.svg)](https://github.com/bachya/simplisafe-python/blob/master/LICENSE)\n[![Code Coverage](https://codecov.io/gh/bachya/simplisafe-python/branch/master/graph/badge.svg)](https://codecov.io/gh/bachya/simplisafe-python)\n[![Maintainability](https://api.codeclimate.com/v1/badges/f46d8b1dcfde6a2f683d/maintainability)](https://codeclimate.com/github/bachya/simplisafe-python/maintainability)\n[![Say Thanks](https://img.shields.io/badge/SayThanks-!-1EAEDB.svg)](https://saythanks.io/to/bachya)\n\n`simplisafe-python` (hereafter referred to as `simplipy`) is a Python3,\n`asyncio`-driven interface to the unofficial SimpliSafe™ API. With it, users can\nget data on their system (including available sensors), set the system state,\nand more.\n\n# Documentation\n\nYou can find complete documentation here: https://simplisafe-python.readthedocs.io\n\n# Contributing\n\n1. [Check for open features/bugs](https://github.com/bachya/simplisafe-python/issues)\n  or [initiate a discussion on one](https://github.com/bachya/simplisafe-python/issues/new).\n2. [Fork the repository](https://github.com/bachya/simplisafe-python/fork).\n3. (_optional, but highly recommended_) Create a virtual environment: `python3 -m venv .venv`\n4. (_optional, but highly recommended_) Enter the virtual environment: `source ./.venv/bin/activate`\n5. Install the dev environment: `script/setup`\n6. Code your new feature or bug fix.\n7. Write tests that cover your new functionality.\n8. Run tests and ensure 100% code coverage: `script/test`\n9. Update `README.md` with any new documentation.\n10. Add yourself to `AUTHORS.md`.\n11. Submit a pull request!\n',
    'author': 'Aaron Bach',
    'author_email': 'bachya1208@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/bachya/simplisafe-python',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8.0,<4.0.0',
}


setup(**setup_kwargs)
