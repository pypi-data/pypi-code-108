# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['djangostreetmap',
 'djangostreetmap.management.commands',
 'djangostreetmap.migrations']

package_data = \
{'': ['*'], 'djangostreetmap': ['templates/*']}

install_requires = \
['osmflex>=0.1.2,<0.2.0']

setup_kwargs = {
    'name': 'djangostreetmap',
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
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
