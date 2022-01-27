# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['griddingmachine']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.0,<2.0', 'toml>=0.10,<0.11']

setup_kwargs = {
    'name': 'python-griddingmachine',
    'version': '0.1.2',
    'description': 'GriddingMachine - a database and tool for earth system modeling',
    'long_description': None,
    'author': 'Yujie Wang',
    'author_email': 'jesiner@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
