# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pyob', 'pyob.exceptions', 'pyob.mixins', 'pyob.tools', 'pyob.utils']

package_data = \
{'': ['*']}

install_requires = \
['typeguard>=2.12.1,<3.0.0']

setup_kwargs = {
    'name': 'pyob',
    'version': '0.2.1',
    'description': 'A high-level runtime object manager for Python 3 and above.',
    'long_description': None,
    'author': 'khunspoonzi',
    'author_email': 'khunspoonzi@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
