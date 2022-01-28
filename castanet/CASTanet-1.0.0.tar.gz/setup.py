# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['castanet']

package_data = \
{'': ['*']}

install_requires = \
['libcst>=0.4.0,<0.5.0', 'typer[all]>=0.4.0,<0.5.0']

entry_points = \
{'console_scripts': ['castanet = main:app']}

setup_kwargs = {
    'name': 'castanet',
    'version': '1.0.0',
    'description': 'Program to identify different syntax in Python programs',
    'long_description': None,
    'author': 'Thomas Antle, Caden Hinckley, Maddy Kapfhammer, Bailey Matrascia, Nolan Thompson',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
