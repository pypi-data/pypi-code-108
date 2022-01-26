# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['gleam']

package_data = \
{'': ['*']}

install_requires = \
['astropy>=4.0.1,<5.0.0',
 'click>=7.1.1,<8.0.0',
 'colorama>=0.4.3,<0.5.0',
 'lmfit>=1.0.0,<2.0.0',
 'matplotlib>=3.2.1,<4.0.0',
 'numpy>=1.18.2,<2.0.0',
 'pydantic>=1.5,<2.0',
 'pyyaml>=5.3.1,<6.0.0']

entry_points = \
{'console_scripts': ['gleam = gleam:pipeline']}

setup_kwargs = {
    'name': 'astro-gleam',
    'version': '1.1.0',
    'description': 'Galaxy Line Emission and Absorption Modeling',
    'long_description': None,
    'author': 'Andra Stroe',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
