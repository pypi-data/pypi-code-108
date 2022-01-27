# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['kapla', 'kapla.cli']

package_data = \
{'': ['*']}

install_requires = \
['colorama<1.0.0',
 'loguru<1.0.0',
 'pydantic>=1.0.0,<2.0.0',
 'python-on-whales<1.0.0',
 'rich>=11.0.0,<12.0.0',
 'stdlib-list<1.0.0',
 'tomlkit<1.0.0',
 'typer<1.0.0']

setup_kwargs = {
    'name': 'kapla-cli-core',
    'version': '3.6.1',
    'description': '',
    'long_description': None,
    'author': 'Guillaume Charbonnier',
    'author_email': 'guillaume.charbonnier@araymond.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
