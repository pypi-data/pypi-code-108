# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['holeysheet']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0',
 'pydantic>=1.8.2,<2.0.0',
 'pylightxl>=1.58,<2.0',
 'xlrd>=2.0.1,<3.0.0']

setup_kwargs = {
    'name': 'holeysheet',
    'version': '0.1.2',
    'description': '',
    'long_description': None,
    'author': 'Nico Ekkart',
    'author_email': 'nekkart@crunchanalytics.be',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
