# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['skit_calls']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0',
 'aiofiles>=0.8.0,<0.9.0',
 'aiohttp>=3.8.1,<4.0.0',
 'loguru>=0.5.3,<0.6.0',
 'pandas>=1.3.5,<2.0.0',
 'toml>=0.10.2,<0.11.0',
 'tqdm>=4.62.3,<5.0.0']

entry_points = \
{'console_scripts': ['skit-calls = skit_calls.cli:main']}

setup_kwargs = {
    'name': 'skit-calls',
    'version': '0.1.6',
    'description': 'Library to fetch calls from a given environment.',
    'long_description': None,
    'author': 'ltbringer',
    'author_email': 'amresh.venugopal@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/skit-ai/skit-calls',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
