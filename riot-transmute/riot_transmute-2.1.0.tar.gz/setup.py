# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['riot_transmute',
 'riot_transmute.common',
 'riot_transmute.v4',
 'riot_transmute.v5']

package_data = \
{'': ['*']}

install_requires = \
['lol-dto>=2.0.0,<3.0.0']

setup_kwargs = {
    'name': 'riot-transmute',
    'version': '2.1.0',
    'description': 'Transmute Riot API objects to the community-defined DTO',
    'long_description': None,
    'author': 'mrtolkien',
    'author_email': 'gary.mialaret@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
