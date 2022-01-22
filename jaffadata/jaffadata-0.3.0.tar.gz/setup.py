# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['jaffadata', 'jaffadata.core', 'jaffadata.datasets']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.21.3,<2.0.0', 'pandas>=1.3.4,<2.0.0']

setup_kwargs = {
    'name': 'jaffadata',
    'version': '0.3.0',
    'description': 'A library for working with audio datasets in ML',
    'long_description': None,
    'author': 'Turab Iqbal',
    'author_email': 't.iqbal@surrey.ac.uk',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/tqbl/jaffadata',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
