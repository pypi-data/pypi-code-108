# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pgkit',
 'pgkit.application',
 'pgkit.application.models',
 'pgkit.application.templates',
 'pgkit.cli',
 'pgkit.cli.commands']

package_data = \
{'': ['*']}

install_requires = \
['Jinja2>=2.11.2,<3.0.0',
 'PyYAML>=6.0,<7.0',
 'click>=7.1.2,<8.0.0',
 'python-dateutil>=2.8.1,<3.0.0',
 'pytz>=2021.1,<2022.0',
 'tinydb>=4.3.0,<5.0.0']

entry_points = \
{'console_scripts': ['pgkit = pgkit.cli.cli:main']}

setup_kwargs = {
    'name': 'pgkit',
    'version': '2.1.6',
    'description': '',
    'long_description': None,
    'author': 'Sadegh Hayeri',
    'author_email': 'hayerisadegh@gmail.com',
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
