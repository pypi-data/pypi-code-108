# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['jetpack',
 'jetpack._remote',
 'jetpack._runtime',
 'jetpack._task',
 'jetpack.cmd',
 'jetpack.config',
 'jetpack.console',
 'jetpack.console.commands',
 'jetpack.models',
 'jetpack.models.core',
 'jetpack.models.runtime',
 'jetpack.proto.runtime.v1alpha1']

package_data = \
{'': ['*']}

install_requires = \
['cleo>=1.0.0a4,<2.0.0',
 'click>=8.0.3,<9.0.0',
 'cronitor>=4.2.0,<5.0.0',
 'grpcio>=1.43.0,<2.0.0',
 'jsonpickle>=2.0.0,<3.0.0',
 'protobuf>=3.17.0,<4.0.0',
 'redis-namespace>=3.0.1,<4.0.0',
 'redis==3.0.1',
 'schedule>=1.1.0,<2.0.0']

entry_points = \
{'console_scripts': ['jetpack-sdk = jetpack:run']}

setup_kwargs = {
    'name': 'jetpack-io',
    'version': '0.5.1.dev202201251643109094',
    'description': 'Python SDK for Jetpack.io',
    'long_description': '### Jetpack SDK\n',
    'author': 'jetpack.io',
    'author_email': 'hello@jetpack.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://www.jetpack.io',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
