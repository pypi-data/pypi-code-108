# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['wyzeapy', 'wyzeapy.services']

package_data = \
{'': ['*']}

install_requires = \
['aiodns>=3.0.0,<4.0.0',
 'aiohttp>=3.7,<4.0',
 'cchardet>=2.1.7,<3.0.0',
 'pycryptodome>=3.12.0,<4.0.0']

setup_kwargs = {
    'name': 'wyzeapy',
    'version': '0.5.6a0',
    'description': 'A library for interacting with Wyze devices',
    'long_description': None,
    'author': 'Joshua Mulliken',
    'author_email': 'joshua@mulliken.net',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
