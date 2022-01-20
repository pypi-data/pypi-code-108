# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nteu_corporate_engine']

package_data = \
{'': ['*']}

install_requires = \
['OpenNMT-py==1.1.0',
 'aiohttp>=3.6.3,<4.0.0',
 'pangeamt-nlp>=1.0.0,<2.0.0',
 'pangeamt-toolkit>=3.57.0,<4.0.0',
 'prettytable>=1.0.1,<2.0.0',
 'torch==1.5.0']

setup_kwargs = {
    'name': 'nteu-corporate-engine',
    'version': '0.1.9',
    'description': 'NTEU model wrapper for corporate injection',
    'long_description': None,
    'author': 'Your Name',
    'author_email': 'you@example.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
