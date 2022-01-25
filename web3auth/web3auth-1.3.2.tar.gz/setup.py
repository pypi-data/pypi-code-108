# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['web3auth']

package_data = \
{'': ['*']}

install_requires = \
['eip712-structs>=1.1.0,<2.0.0',
 'eth-account>=0.5.6,<0.6.0',
 'eth-utils>=1.9.5,<2.0.0',
 'python-jose[cryptography]>=3.3.0,<4.0.0']

setup_kwargs = {
    'name': 'web3auth',
    'version': '1.3.2',
    'description': 'A web3-based authentication library for python',
    'long_description': None,
    'author': 'Павел Жуков',
    'author_email': '33721692+LeaveMyYard@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
