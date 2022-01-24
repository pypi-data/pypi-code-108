# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['taktile_auth', 'taktile_auth.entities']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0', 'pydantic>=1.8.2,<2.0.0']

setup_kwargs = {
    'name': 'taktile-auth',
    'version': '0.0.1a1',
    'description': 'Auth Package for Taktile',
    'long_description': None,
    'author': 'Taktile GmbH',
    'author_email': 'devops@taktile.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.1,<4.0.0',
}


setup(**setup_kwargs)
