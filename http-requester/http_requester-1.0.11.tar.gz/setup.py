# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['http_requester']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.6.2,<4.0.0',
 'asyncio>=3.4.3,<4.0.0',
 'nest_asyncio>=1.4.0,<2.0.0',
 'pydantic>=1.6.1,<2.0.0',
 'requests>=2.26.0,<3.0.0',
 'yarl>=1.6.0,<2.0.0']

setup_kwargs = {
    'name': 'http-requester',
    'version': '1.0.11',
    'description': 'Simple interface for building HTTP API requests.',
    'long_description': None,
    'author': "Ryan O'Rourke",
    'author_email': 'ryan.orourke@welocalize.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
