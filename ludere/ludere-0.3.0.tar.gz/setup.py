# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ludere']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'ludere',
    'version': '0.3.0',
    'description': 'Toy DI framework',
    'long_description': None,
    'author': 'Vlad Smirnov',
    'author_email': 'gnudeb0@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
