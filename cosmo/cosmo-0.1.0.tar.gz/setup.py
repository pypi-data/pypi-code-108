# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cosmo']

package_data = \
{'': ['*']}

install_requires = \
['loguru>=0.5.3,<0.6.0']

setup_kwargs = {
    'name': 'cosmo',
    'version': '0.1.0',
    'description': "A web server I'm working on for fun.",
    'long_description': None,
    'author': 'Kronifer',
    'author_email': '44979306+Kronifer@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
