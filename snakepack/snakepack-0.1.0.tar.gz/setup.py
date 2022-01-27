# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['snakepack',
 'snakepack.analyzers',
 'snakepack.analyzers.python',
 'snakepack.assets',
 'snakepack.bundlers',
 'snakepack.config',
 'snakepack.loaders',
 'snakepack.packagers',
 'snakepack.transformers',
 'snakepack.transformers.python']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0',
 'boltons>=21.0.0,<22.0.0',
 'click>=8.0.3,<9.0.0',
 'cloudpickle>=2.0.0,<3.0.0',
 'libcst>=0.3.21,<0.4.0',
 'loky>=3.0.0,<4.0.0',
 'modulegraph>=0.19.2,<0.20.0',
 'pydantic>=1.8.2,<2.0.0',
 'stdlib-list>=0.8.0,<0.9.0']

entry_points = \
{'console_scripts': ['snakepack = snakepack.app:snakepack']}

setup_kwargs = {
    'name': 'snakepack',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Jochen Van de Velde',
    'author_email': 'mail@jochenvandevelde.be',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<=3.10',
}


setup(**setup_kwargs)
