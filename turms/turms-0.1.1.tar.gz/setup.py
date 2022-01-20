# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['turms',
 'turms.cli',
 'turms.parser',
 'turms.plugins',
 'turms.processor',
 'turms.wards']

package_data = \
{'': ['*']}

install_requires = \
['graphql-core>=3.2.0,<4.0.0', 'pydantic>=1.9.0,<2.0.0', 'rich>=11.0.0,<12.0.0']

entry_points = \
{'console_scripts': ['turms = turms.cli.main:entrypoint']}

setup_kwargs = {
    'name': 'turms',
    'version': '0.1.1',
    'description': 'graphql-codegen',
    'long_description': None,
    'author': 'jhnnsrs',
    'author_email': 'jhnnsrs@gmail.com',
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
