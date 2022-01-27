# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['jupyterbot', 'jupyterbot.robot']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'jupyterbot',
    'version': '0.0.21',
    'description': '',
    'long_description': None,
    'author': 'Johnata Brayan',
    'author_email': 'johnatabrayan@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
