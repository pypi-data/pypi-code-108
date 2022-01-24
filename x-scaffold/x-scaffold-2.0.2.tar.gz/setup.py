# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['x_scaffold', 'x_scaffold.plugins']

package_data = \
{'': ['*']}

install_requires = \
['GitPython>=3.1.24,<4.0.0',
 'Jinja2==3.0.3',
 'PyGithub>=1.55,<2.0',
 'PyYAML>=6.0,<7.0',
 'click>=7.0.0,<8.0.0',
 'ruamel.yaml>=0.17.20,<0.18.0']

entry_points = \
{'console_scripts': ['xscaffold = x_scaffold.cli:cli']}

setup_kwargs = {
    'name': 'x-scaffold',
    'version': '2.0.2',
    'description': 'Used to scaffold directories or GitHub repositories.',
    'long_description': None,
    'author': 'Dan Clayton',
    'author_email': 'dan@azwebmaster.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
