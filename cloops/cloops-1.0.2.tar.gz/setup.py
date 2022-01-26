# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cloops']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'cloops',
    'version': '1.0.2',
    'description': 'dfgdfg',
    'long_description': None,
    'author': 'Your Name',
    'author_email': 'you@example.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)
