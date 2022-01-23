# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tordle']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.0.3,<9.0.0',
 'isort>=5.10.1,<6.0.0',
 'rich>=11.0.0,<12.0.0',
 'textual>=0.1.14,<0.2.0',
 'toml>=0.10.2,<0.11.0',
 'yapf>=0.32.0,<0.33.0']

entry_points = \
{'console_scripts': ['tordle = tordle.tordle:main']}

setup_kwargs = {
    'name': 'tordle',
    'version': '0.1.1',
    'description': 'A command-line word game.',
    'long_description': None,
    'author': 'Justin Sybrandt',
    'author_email': 'justin@sybrandt.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
