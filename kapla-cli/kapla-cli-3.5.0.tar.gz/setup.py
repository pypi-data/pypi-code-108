# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['kapla', 'kapla.cli', 'kapla.cli.commands', 'kapla.docker']

package_data = \
{'': ['*'], 'kapla.cli': ['defaults/*']}

install_requires = \
['black>=21.7-beta.0,<22.0',
 'colorama>=0.4.4,<0.5.0',
 'commitizen>=2.18.0,<3.0.0',
 'cryptography==3.4.8',
 'flake8>=3.9.2,<4.0.0',
 'isort>=5.9.3,<6.0.0',
 'mypy>=0.931,<0.932',
 'pre-commit>=2.14.0,<3.0.0',
 'pytest-cov>=2.12.1,<3.0.0',
 'pytest>=6.2.4,<7.0.0',
 'snakeviz>=2.1.0,<3.0.0',
 'twine>=3.4.2,<4.0.0']

entry_points = \
{'console_scripts': ['k = kapla.cli.app:app']}

setup_kwargs = {
    'name': 'kapla-cli',
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
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
