# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['umm', 'umm.cli', 'umm.server', 'umm.utils']

package_data = \
{'': ['*'], 'umm': ['resources/*']}

install_requires = \
['PyYAML>=5.4.1,<6.0.0',
 'Pygments>=2.10.0,<3.0.0',
 'aiohttp>=3.7.4,<4.0.0',
 'click>=8.0.1,<9.0.0',
 'psutil>=5.9.0,<6.0.0',
 'pydantic>=1.8.2,<2.0.0',
 'requests>=2.26.0,<3.0.0',
 'setuptools>=57.5.0,<58.0.0']

entry_points = \
{'console_scripts': ['umm = umm.cli:umm']}

setup_kwargs = {
    'name': 'umm-cli-helper',
    'version': '0.5.0',
    'description': 'CLI tool for figuring out forgotten CLI commands through search and tagging',
    'long_description': None,
    'author': 'Zachary Coleman',
    'author_email': 'zacharywcoleman@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/zachcoleman/umm-cli-helper',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4',
}


setup(**setup_kwargs)
