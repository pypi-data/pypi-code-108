# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['memetext']

package_data = \
{'': ['*']}

install_requires = \
['Pillow>=8.2.0,<9.0.0', 'click>=7.1.2,<8.0.0']

entry_points = \
{'console_scripts': ['memetext = memetext.memetext:main']}

setup_kwargs = {
    'name': 'memetext',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Ryan Townshend',
    'author_email': 'citizen.townshend@gmail.com',
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
