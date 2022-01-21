# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ragdoll']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'ragdoll',
    'version': '0.2.0',
    'description': '',
    'long_description': None,
    'author': 'Aaron Zhang',
    'author_email': 'rabbit.aaron@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/rabbit-aaron/ragdoll',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
