# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pymint', 'pymint.antlrgen', 'pymint.constraints']

package_data = \
{'': ['*']}

install_requires = \
['antlr4-python3-runtime>=4.8,<5.0',
 'install>=1.3.3,<2.0.0',
 'parchmint>=0.2.11,<0.3.0',
 'pip>=20.2.2,<21.0.0']

entry_points = \
{'console_scripts': ['mint-tools = pymint.cmdline:main']}

setup_kwargs = {
    'name': 'pymint',
    'version': '0.2.16',
    'description': 'MINT is a human readable language to describe Microfluidic Hardware Netlists. MINT is the name of the Microfluidic Netlist language used to describe microfluidic devices for Fluigi to place and route. Mint is a flavor of (MHDL) Microfluidic Hardware Description Language that can be used to represent Microfluidic Circuits.',
    'long_description': None,
    'author': 'Radhakrishna Sanka',
    'author_email': 'rkrishnasanka@gmail.com',
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
