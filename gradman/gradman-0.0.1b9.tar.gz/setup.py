# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['gradman']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.21.5,<2.0.0']

setup_kwargs = {
    'name': 'gradman',
    'version': '0.0.1b9',
    'description': 'Baby Deep Learning Library',
    'long_description': None,
    'author': 'tanmoyio',
    'author_email': 'tanmoyf2@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
