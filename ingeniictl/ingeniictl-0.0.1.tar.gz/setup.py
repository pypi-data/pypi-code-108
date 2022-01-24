# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ingeniictl', 'ingeniictl.cli.infra']

package_data = \
{'': ['*']}

install_requires = \
['typer>=0.4.0,<0.5.0']

entry_points = \
{'console_scripts': ['ingeniictl = ingeniictl.main:app']}

setup_kwargs = {
    'name': 'ingeniictl',
    'version': '0.0.1',
    'description': "Ingenii's Swiss Army Knife",
    'long_description': "# ingeniictl - Ingenii's Swiss Army Knife\n\n## Overview\n\nTBD\n\n## Usage\n\n## Contribute",
    'author': 'Teodor Kostadinov',
    'author_email': 'teodor@ingenii.dev',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
