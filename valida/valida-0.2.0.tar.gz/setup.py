# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['valida']

package_data = \
{'': ['*']}

install_requires = \
['ruamel.yaml>=0.17.20,<0.18.0']

setup_kwargs = {
    'name': 'valida',
    'version': '0.2.0',
    'description': 'Comprehensive validation library for nested data structures.',
    'long_description': None,
    'author': 'Adam J. Plowman',
    'author_email': 'adam.jp@live.co.uk',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<3.11',
}


setup(**setup_kwargs)
