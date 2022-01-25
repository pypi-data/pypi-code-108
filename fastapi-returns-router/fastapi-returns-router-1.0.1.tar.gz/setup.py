# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fastapi_returns_router']

package_data = \
{'': ['*']}

install_requires = \
['fastapi>=0.72.0,<0.73.0', 'returns>=0.18.0,<0.19.0']

setup_kwargs = {
    'name': 'fastapi-returns-router',
    'version': '1.0.1',
    'description': 'This FastAPI Router Implementation bridges the gap between FastAPI and Returns',
    'long_description': "# FastAPI Returns Router\n\n## Description\n\nThis Project is a simple layer that allows Returns to work within\nFastAPI. It simply allows a person to return the base return's containers\nfrom a route. It is a drop-in replacement for the normal FastAPI router.\n\nIt does require that the route functions have a typed return function.",
    'author': 'Ian Kollipara',
    'author_email': 'ian.kollipara@cune.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ikollipara/fastapi-returns',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
