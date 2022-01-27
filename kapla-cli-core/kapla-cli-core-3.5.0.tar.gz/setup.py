# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['kapla', 'kapla.cli']

package_data = \
{'': ['*']}

install_requires = \
['loguru>=0.5.3,<0.6.0',
 'pydantic>=1.8.2,<2.0.0',
 'python-on-whales>=0.24.0,<0.25.0',
 'rich>=10.7.0,<11.0.0',
 'stdlib-list>=0.8.0,<0.9.0',
 'tomlkit>=0.7.2,<0.8.0',
 'typer>=0.3.2,<0.4.0',
 'types-PyYAML>=5.4.6,<6.0.0',
 'types-pkg-resources>=0.1.3,<0.2.0']

setup_kwargs = {
    'name': 'kapla-cli-core',
    'version': '3.5.0',
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
