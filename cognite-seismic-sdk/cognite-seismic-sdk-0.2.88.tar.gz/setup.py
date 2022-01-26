# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cognite',
 'cognite.seismic',
 'cognite.seismic._api',
 'cognite.seismic.data_classes',
 'cognite.seismic.protos',
 'cognite.seismic.protos.v1']

package_data = \
{'': ['*']}

install_requires = \
['deprecation>=2.1.0,<3.0.0',
 'grpcio-tools>=1.31,<2.0',
 'grpcio>=1.31,<2.0',
 'numpy>=1.17,<2.0',
 'oauthlib>=3.1.1,<4.0.0',
 'protobuf>=3.12,<4.0',
 'python-dateutil>=2.8,<3.0',
 'requests>=2.26.0,<3.0.0',
 'requests_oauthlib>=1.3.0,<2.0.0',
 'six>=1.14,<2.0',
 'urllib3>=1.24,<2.0']

extras_require = \
{'tox_deps': ['msal>=1.15.0,<2.0.0', 'shapely>=1.7,<2.0']}

setup_kwargs = {
    'name': 'cognite-seismic-sdk',
    'version': '0.2.88',
    'description': '',
    'long_description': None,
    'author': 'cognite',
    'author_email': 'support@cognite.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6.1,<4.0.0',
}


setup(**setup_kwargs)
