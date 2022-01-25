# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['utilityfunc']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'utilityfunc',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Your Name',
    'author_email': 'you@example.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
