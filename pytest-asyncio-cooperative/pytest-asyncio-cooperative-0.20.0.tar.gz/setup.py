# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pytest_asyncio_cooperative']

package_data = \
{'': ['*']}

entry_points = \
{'pytest11': ['asyncio-cooperative = pytest_asyncio_cooperative.plugin']}

setup_kwargs = {
    'name': 'pytest-asyncio-cooperative',
    'version': '0.20.0',
    'description': 'Run all your asynchronous tests cooperatively.',
    'long_description': None,
    'author': 'Willem Thiart',
    'author_email': 'himself@willemthiart.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.7',
}


setup(**setup_kwargs)
