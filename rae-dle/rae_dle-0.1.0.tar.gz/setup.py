# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['rae_dle']

package_data = \
{'': ['*']}

install_requires = \
['selenium>=4.1.0,<5.0.0']

setup_kwargs = {
    'name': 'rae-dle',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Pedro Sanchez',
    'author_email': 'pedrosanchez757@hotmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
