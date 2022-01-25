# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['taktile_client',
 'taktile_client.arrow',
 'taktile_client.arrow.serialize',
 'taktile_client.rest',
 'taktile_client.rest.serialize']

package_data = \
{'': ['*']}

install_requires = \
['pydantic>=1.8.2,<2.0.0',
 'requests>=2.26.0,<3.0.0',
 'taktile-types>=0.12.0,<1.0.0',
 'tenacity>=8.0.1,<9.0.0']

extras_require = \
{'arrow': ['numpy>=1.21,<2.0',
           'pandas>=1.3,<2.0',
           'pyarrow>=6.0,<7.0',
           'certifi==2021.10.8']}

setup_kwargs = {
    'name': 'taktile-client',
    'version': '1.0.0b2',
    'description': 'A lightweight client to call models deployed on Taktile.',
    'long_description': None,
    'author': 'Taktile GmbH',
    'author_email': 'devops@taktile.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7.1,<4.0.0',
}


setup(**setup_kwargs)
