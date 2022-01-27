# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['poetry_rak']

package_data = \
{'': ['*']}

install_requires = \
['pandas>=1.4.0,<2.0.0']

entry_points = \
{'console_scripts': ['run = display:display1']}

setup_kwargs = {
    'name': 'poetry-rak',
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
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8.11,<4.0.0',
}


setup(**setup_kwargs)
