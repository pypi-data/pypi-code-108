# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['qm',
 'qm.grpc',
 'qm.grpc.quantum_simulator',
 'qm.grpc_client_interceptor',
 'qm.pb',
 'qm.program',
 'qm.qua',
 'qm.qua_future',
 'qm.results',
 'qm.simulate']

package_data = \
{'': ['*']}

install_requires = \
['betterproto>=1.2.5,<2.0.0',
 'grpcio>=1.39.0,<2.0.0',
 'marshmallow-polyfield>=5.7,<6.0',
 'marshmallow>=3.0.0,<4.0.0',
 'numpy>=1.17.0,<2.0.0',
 'protobuf>=3.17.3,<4.0.0',
 'qua>=0.1.0,<0.2.0']

setup_kwargs = {
    'name': 'qm-qua',
    'version': '0.3.6',
    'description': 'QUA language SDK to control a Quantum Computer',
    'long_description': '\n# QUA SDK\n\nQUA language SDK to control a Quantum Computer',
    'author': 'Tal Shani',
    'author_email': 'tal@quantum-machines.co',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
