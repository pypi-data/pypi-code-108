# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['agal']

package_data = \
{'': ['*']}

install_requires = \
['cryptography>=3.4.7,<4.0.0', 'fire>=0.3.1,<0.4.0', 'websockets>=10.1,<11.0']

entry_points = \
{'console_scripts': ['agal-cli = agal.cli:main',
                     'agal-server = agal.server:main']}

setup_kwargs = {
    'name': 'agal',
    'version': '0.0.5',
    'description': '',
    'long_description': None,
    'author': 'Gongziting Tech Ltd.',
    'author_email': None,
    'url': 'https://github.com/gzttech/agal',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
