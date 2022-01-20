# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['graphlib']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'topological-sort-backport',
    'version': '0.4.0',
    'description': '',
    'long_description': None,
    'author': 'Jonas Bulik',
    'author_email': 'jonas@bulik.dev',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/MrGreenTea/topological-sort-backport',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<3.9',
}


setup(**setup_kwargs)
