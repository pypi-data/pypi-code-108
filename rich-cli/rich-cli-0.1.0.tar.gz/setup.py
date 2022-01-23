# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['rich_cli']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.0.3,<9.0.0', 'rich>=11.0.0,<12.0.0']

entry_points = \
{'console_scripts': ['rich = rich_cli.__main__:run']}

setup_kwargs = {
    'name': 'rich-cli',
    'version': '0.1.0',
    'description': 'Command Line Interface to Rich',
    'long_description': None,
    'author': 'Will McGugan',
    'author_email': 'willmcgugan@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
