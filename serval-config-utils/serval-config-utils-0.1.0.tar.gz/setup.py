# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['configutils']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0', 'mergedeep>=1.3.4,<2.0.0']

setup_kwargs = {
    'name': 'serval-config-utils',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Thibault Simonetto',
    'author_email': 'thibault.simonetto@uni.lu',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
