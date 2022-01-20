# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['jcutil',
 'jcutil.chalk',
 'jcutil.core',
 'jcutil.dba',
 'jcutil.drivers',
 'jcutil.server']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0',
 'aiohttp>=3.8.1,<4.0.0',
 'click>=8.0.3,<9.0.0',
 'colorama>=0.4.4,<0.5.0',
 'jcramda>=1.0.6,<2.0.0',
 'pycryptodomex>=3.11.0,<4.0.0',
 'pymongo>=4.0,<5.0',
 'python-consul>=1.1.0,<2.0.0',
 'python-dotenv>=0.19.2,<0.20.0',
 'redis-py-cluster>=2.1.3,<3.0.0']

setup_kwargs = {
    'name': 'jcutil',
    'version': '1.0.4',
    'description': "Some python util tolls in one package for your web app'",
    'long_description': None,
    'author': 'Jochen.He',
    'author_email': 'thjl@hotmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
