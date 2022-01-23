# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['lavalink']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3,<4', 'nextcord']

setup_kwargs = {
    'name': 'useless-lavalink',
    'version': '1.3.7.2',
    'description': 'A fork of Red-Lavalink for useless_bot',
    'long_description': None,
    'author': 'MRvillager',
    'author_email': 'mrvillager.dev@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
