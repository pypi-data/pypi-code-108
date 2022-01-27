# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tawnyapi', 'tawnyapi.vision']

package_data = \
{'': ['*']}

install_requires = \
['aiofiles>=0.7.0,<0.8.0',
 'aiohttp>=3.7.4,<4.0.0',
 'imutils>=0.5.4,<0.6.0',
 'numpy==1.19.5',
 'opencv-python==4.4.0.46',
 'tensorflow>=2.6.0,<3.0.0',
 'toml>=0.10.2,<0.11.0',
 'typer>=0.3.2,<0.4.0']

setup_kwargs = {
    'name': 'tawnyapi',
    'version': '0.1.8',
    'description': '',
    'long_description': None,
    'author': 'TAWNY GmbH',
    'author_email': 'support@tawny.ai',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
