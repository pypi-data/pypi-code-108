# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pygismeteo_base', 'pygismeteo_base.models']

package_data = \
{'': ['*']}

install_requires = \
['pydantic>=1.8.2,<2.0.0']

setup_kwargs = {
    'name': 'pygismeteo-base',
    'version': '2.1.0',
    'description': 'Base for pygismeteo and aiopygismeteo',
    'long_description': '# pygismeteo-base\n\n[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/monosans/pygismeteo-base/blob/main/LICENSE)\n\nБаза для [pygismeteo](https://github.com/monosans/pygismeteo) и [aiopygismeteo](https://github.com/monosans/aiopygismeteo).\n',
    'author': 'monosans',
    'author_email': 'hsyqixco@protonmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/monosans/pygismeteo-base',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
