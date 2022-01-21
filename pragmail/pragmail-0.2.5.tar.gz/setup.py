# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pragmail']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'pragmail',
    'version': '0.2.5',
    'description': 'Simple library for retrieving and repackaging email messages.',
    'long_description': '# pragmail [![python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/release/python-397/)\n\npragmail is a library for retrieving email messages for other useful software applications.\n\nIt extends Python\'s built-in modules for internet protocols and support, maintaining the same degree of user flexibility.\n\nExample usage:\n```python\n>>> import pragmail\n>>> client = pragmail.Client("imap.domain.com")\n>>> client.login("username", "password")\n(\'OK\', [b\'username authenticated (Success)\'])\n>>> client.select("INBOX")\n(\'OK\', [b\'1357\'])\n>>> client.imap4.search(None, \'FROM\', \'"John Smith"\')\n(\'OK\', [b\'245 248 257 259\'])\n>>> client.imap4.close()\n(\'OK\', [b\'Returned to authenticated state. (Success)\'])\n>>> client.imap4.logout()\n(\'BYE\', [b\'LOGOUT Requested\'])\n```\n\npragmail also equips you with several utility functions and a few useful methods for managing retrieved email messages. Please refer to the documentation for details.\n\n# Installing\n\npragmail can be installed with pip:\n```\n$ python -m pip install pragmail\n```\n\nYou can get the latest source code from GitHub:\n```\n$ git clone git://github.com/huenique/pragmail.git\n$ cd pragmail/\n$ poetry install\n```\n\n# Documentation\n\nUsage and reference documentation is found [here](./docs).\n\n# Contributing\n\nCheck the [contributing guide](./.github/CONTRIBUTING.md) to learn more about the development process and how you can test your changes.\n',
    'author': 'Hju Kneyck Flores',
    'author_email': 'hjucode@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
