# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['amora', 'amora.providers', 'amora.tests']

package_data = \
{'': ['*'], 'amora': ['target/*', 'templates/*']}

install_requires = \
['Jinja2>=2.11.3,<3.0.0',
 'SQLAlchemy[mypy]>=1.4.27,<2.0.0',
 'matplotlib>=3.4.2,<4.0.0',
 'networkx[all]>=2.6.3,<3.0.0',
 'numpy>=1.21.1,<2.0.0',
 'pandas>=1.3.0,<2.0.0',
 'pytest-xdist[psutil]>=2.5.0,<3.0.0',
 'pytest>=6.2.5,<7.0.0',
 'rich>=10.13.0,<11.0.0',
 'sqlalchemy-bigquery>=1.2,<2.0',
 'sqlmodel>=0.0.4,<0.0.5',
 'sqlparse>=0.3.1,<0.4.0',
 'typer[all]>=0.4.0,<0.5.0']

entry_points = \
{'console_scripts': ['amora = amora.cli:main']}

setup_kwargs = {
    'name': 'amora',
    'version': '0.1.7rc3',
    'description': 'Amora Data Build Tool',
    'long_description': None,
    'author': 'diogommartins',
    'author_email': 'diogo.martins@stone.com.br',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9.6,<3.10',
}


setup(**setup_kwargs)
