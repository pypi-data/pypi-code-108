# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['weni',
 'weni.protobuf',
 'weni.protobuf.connect',
 'weni.protobuf.flows',
 'weni.protobuf.integrations',
 'weni.protobuf.intelligence',
 'weni.protobuf.wpp_router']

package_data = \
{'': ['*']}

install_requires = \
['grpcio>=1.39.0,<2.0.0', 'protobuf>=3.17.3,<4.0.0']

setup_kwargs = {
    'name': 'weni-protobuffers',
    'version': '1.2.8',
    'description': 'Protocol Buffers for Weni Platform',
    'long_description': None,
    'author': 'João Carlos',
    'author_email': 'jcbalmeida@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
