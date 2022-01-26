# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['osmflex',
 'osmflex.management',
 'osmflex.management.commands',
 'osmflex.migrations']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'osmflex',
    'version': '0.1.2',
    'description': '',
    'long_description': None,
    'author': 'Joshua Brooks',
    'author_email': 'josh.vdbroek@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
