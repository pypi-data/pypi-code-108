# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['bridgebots']

package_data = \
{'': ['*']}

install_requires = \
['marshmallow>=3.12.1,<4.0.0']

setup_kwargs = {
    'name': 'bridgebots',
    'version': '0.0.10.dev0',
    'description': 'Data processing for Contract Bridge',
    'long_description': None,
    'author': 'Forrest Rice',
    'author_email': 'forrest.d.rice@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
