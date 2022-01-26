# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['mockumentary']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'mockumentary',
    'version': '0.0.1',
    'description': 'Safety placeholder',
    'long_description': None,
    'author': 'Prima',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
