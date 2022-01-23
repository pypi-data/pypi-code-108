# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['resolve_name_clash', 'resolve_name_clash.tests']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.0.3,<9.0.0']

entry_points = \
{'console_scripts': ['resolve-name-clash = '
                     'resolve_name_clash.resolve_name_clash:cli']}

setup_kwargs = {
    'name': 'resolve-name-clash',
    'version': '0.1.0',
    'description': 'Simple utility that takes a source file and a destination directory and determines a unique name for the source file in the destination directory that will not clash with any existing file.',
    'long_description': None,
    'author': 'Shyam Pather',
    'author_email': 'shyam.pather@gmail.com',
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
