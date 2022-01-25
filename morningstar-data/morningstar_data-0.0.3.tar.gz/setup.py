# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['morningstar_data']

package_data = \
{'': ['*']}

install_requires = \
['black>=21.12b0,<22.0',
 'coverage>=6.2,<7.0',
 'mypy>=0.931,<0.932',
 'pre-commit>=2.16.0,<3.0.0',
 'pytest>=6.2.5,<7.0.0']

setup_kwargs = {
    'name': 'morningstar-data',
    'version': '0.0.3',
    'description': 'Morningstar Data',
    'long_description': None,
    'author': 'Morningstar, Inc.',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
