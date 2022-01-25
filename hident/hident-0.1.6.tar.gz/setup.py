# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['hident']

package_data = \
{'': ['*']}

install_requires = \
['click-log>=0.3.2,<0.4.0',
 'click>=7.1.2,<8.0.0',
 'pandas>=1.3.5,<2.0.0',
 'prefixcommons>=0.1.9,<0.2.0']

entry_points = \
{'console_scripts': ['hident = hident.hident:hident']}

setup_kwargs = {
    'name': 'hident',
    'version': '0.1.6',
    'description': '',
    'long_description': None,
    'author': 'Mark A. Miller',
    'author_email': 'mamillerpa@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
