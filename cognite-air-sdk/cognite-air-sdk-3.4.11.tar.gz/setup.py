# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': '.'}

packages = \
['cognite', 'cognite.air']

package_data = \
{'': ['*']}

install_requires = \
['cognite-sdk>=2.4.2,<3.0.0',
 'pre-commit>=2.7.1,<3.0.0',
 'ruamel.yaml>=0.16.12,<0.17.0']

setup_kwargs = {
    'name': 'cognite-air-sdk',
    'version': '3.4.11',
    'description': 'Client library for AIR, built on top of Cognite Functions in Cognite Data Fusion (CDF)',
    'long_description': None,
    'author': 'Håkon V. Treider',
    'author_email': 'hakon.treider@cognite.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.1,<4.0.0',
}


setup(**setup_kwargs)
