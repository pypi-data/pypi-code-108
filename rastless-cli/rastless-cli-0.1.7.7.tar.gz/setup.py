# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['rastless', 'rastless.cli', 'rastless.core', 'rastless.db']

package_data = \
{'': ['*']}

install_requires = \
['boto3>=1.20.26,<2.0.0',
 'click>=8.0.3,<9.0.0',
 'moto>=2.3.0,<3.0.0',
 'pydantic>=1.9.0,<2.0.0',
 'rasterio>=1.2.10,<2.0.0',
 'rio-cogeo>=3.0.2,<4.0.0',
 'xmltodict>=0.12.0,<0.13.0']

entry_points = \
{'console_scripts': ['rastless = rastless.main:cli']}

setup_kwargs = {
    'name': 'rastless-cli',
    'version': '0.1.7.7',
    'description': 'A cli for managing data and user access for the cloud application rastless',
    'long_description': 'Rastless-CLI\n=================\n\n##### A cli for managing data and user access for the cloud application rastless\n\n\n',
    'author': 'Marcel Siegmann',
    'author_email': 'siegmann@eomap.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
