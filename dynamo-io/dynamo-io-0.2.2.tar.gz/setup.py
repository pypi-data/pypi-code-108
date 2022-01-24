# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dynamo_io',
 'dynamo_io.mock',
 'dynamo_io.recorder',
 'dynamo_io.tests',
 'dynamo_io.tests.mock',
 'dynamo_io.tests.mock.expressions',
 'dynamo_io.tests.reader',
 'dynamo_io.tests.recorder',
 'dynamo_io.tests.writer']

package_data = \
{'': ['*']}

install_requires = \
['boto3>=1.17.21,<2.0.0', 'toml>=0.10.0']

setup_kwargs = {
    'name': 'dynamo-io',
    'version': '0.2.2',
    'description': 'Opinionated single-table library for DynamoDB with in-memory mocking capabilities for unit and scenario testing.',
    'long_description': None,
    'author': 'Scott Ernst',
    'author_email': 'swernst@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
