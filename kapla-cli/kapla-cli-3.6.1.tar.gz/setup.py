# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['kapla', 'kapla.cli', 'kapla.cli.commands', 'kapla.docker']

package_data = \
{'': ['*'], 'kapla.cli': ['defaults/*']}

install_requires = \
['black',
 'commitizen>=2.0.0,<3.0.0',
 'flake8>=4.0.0,<5.0.0',
 'isort>=5.0.0,<6.0.0',
 'kapla-cli-core>=3.4',
 'mypy<1.0.0',
 'pre-commit>=2.0.0,<3.0.0',
 'pytest-cov>=3.0.0,<4.0.0',
 'pytest>=6.0.0,<7.0.0',
 'snakeviz>=2.0.0,<3.0.0',
 'twine>=3.0.0,<4.0.0',
 'types-PyYAML>=6.0.0,<7.0.0',
 'types-pkg-resources<1.0.0']

entry_points = \
{'console_scripts': ['k = kapla.cli.app:app']}

setup_kwargs = {
    'name': 'kapla-cli',
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
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
