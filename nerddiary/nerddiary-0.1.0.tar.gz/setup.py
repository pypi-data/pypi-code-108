# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nerddiary',
 'nerddiary.bots',
 'nerddiary.bots.tgbot',
 'nerddiary.core',
 'nerddiary.core.data',
 'nerddiary.core.poll',
 'nerddiary.core.report',
 'nerddiary.core.user']

package_data = \
{'': ['*']}

install_requires = \
['SQLAlchemy>=1.4.29,<2.0.0',
 'click>=8.0.3,<9.0.0',
 'cryptography>=36.0.1,<37.0.0',
 'pydantic>=1.9.0,<2.0.0',
 'python-telegram-bot>=13.9,<14.0']

entry_points = \
{'console_scripts': ['nerddiary = nerddiary.cli:cli']}

setup_kwargs = {
    'name': 'nerddiary',
    'version': '0.1.0',
    'description': 'A collection of tools to capture and analyze migraines',
    'long_description': '# THe Nerd Diary\n\nWIP\n',
    'author': 'mishamsk',
    'author_email': 'mishamsk@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://nerddiary.app',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
