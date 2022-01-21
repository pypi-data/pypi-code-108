# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tyba_client']

package_data = \
{'': ['*']}

install_requires = \
['dataclasses-json>=0.5.4,<0.6.0',
 'marshmallow>=3.12.1,<4.0.0',
 'pandas>=1.3.2,<2.0.0',
 'requests>=2.25.1,<3.0.0']

setup_kwargs = {
    'name': 'tyba-client',
    'version': '0.1.20',
    'description': 'A Python API client for the Tyba Public API',
    'long_description': '# Tyba API Client',
    'author': 'Tyler Nisonoff',
    'author_email': 'tyler@tybaenergy.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
