# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['arcl']

package_data = \
{'': ['*'], 'arcl': ['docs/*']}

install_requires = \
['click>=7.0,<8.0',
 'cookiecutter>=1.7.2',
 'msal-extensions',
 'msal>=1.10.0,<2.0.0',
 'requests']

entry_points = \
{'console_scripts': ['arcl = arcl.cli:cli']}

setup_kwargs = {
    'name': 'arcl',
    'version': '1.3.1',
    'description': 'The CLI for Archimedes',
    'long_description': None,
    'author': 'Optimeering AS',
    'author_email': 'dev@optimeering.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4',
}


setup(**setup_kwargs)
