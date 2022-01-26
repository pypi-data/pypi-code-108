# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['viewser',
 'viewser.commands',
 'viewser.commands.config',
 'viewser.commands.documentation',
 'viewser.commands.help',
 'viewser.commands.logs',
 'viewser.commands.model',
 'viewser.commands.notebooks',
 'viewser.commands.queryset',
 'viewser.commands.queryset.models',
 'viewser.commands.system',
 'viewser.error_handling',
 'viewser.settings',
 'viewser.storage',
 'viewser.tui',
 'viewser.tui.formatting']

package_data = \
{'': ['*']}

install_requires = \
['PyMonad>=2.4.0,<3.0.0',
 'click>=8.0.1,<9.0.0',
 'colorama>=0.4.4,<0.5.0',
 'crayons>=0.4.0,<0.5.0',
 'docker>=5.0.0,<6.0.0',
 'environs>=9.3.1,<10.0.0',
 'fitin>=0.2.0,<0.3.0',
 'pandas>=1.2.3,<2.0.0',
 'psutil>=5.8.0,<6.0.0',
 'pyarrow>=6.0.1,<7.0.0',
 'pydantic>=1.8.1,<2.0.0',
 'requests>=2.27.1,<3.0.0',
 'strconv>=0.4.2,<0.5.0',
 'tabulate>=0.8.9,<0.9.0',
 'toml>=0.10.2,<0.11.0',
 'toolz>=0.11.1,<0.12.0',
 'views-schema==2.1.1',
 'views-storage>=1.1.0,<2.0.0']

entry_points = \
{'console_scripts': ['viewser = viewser.cli:viewser']}

setup_kwargs = {
    'name': 'viewser',
    'version': '5.9.0',
    'description': '',
    'long_description': None,
    'author': 'peder2911',
    'author_email': 'pglandsverk@gmail.com',
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
