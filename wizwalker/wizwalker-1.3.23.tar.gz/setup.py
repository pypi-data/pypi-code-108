# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['wizwalker',
 'wizwalker.cli',
 'wizwalker.combat',
 'wizwalker.extensions.scripting',
 'wizwalker.file_readers',
 'wizwalker.memory',
 'wizwalker.memory.memory_objects']

package_data = \
{'': ['*']}

install_requires = \
['aioconsole>=0.2.1,<0.3.0',
 'aiofiles>=0.7.0,<0.8.0',
 'aiomonitor>=0.4.5,<0.5.0',
 'appdirs>=1.4.4,<2.0.0',
 'click>=7.1.2,<8.0.0',
 'click_default_group>=1.2.2,<2.0.0',
 'janus>=0.6.1,<0.7.0',
 'loguru>=0.5.1,<0.6.0',
 'pefile>=2021.5.24,<2022.0.0',
 'pymem==1.8.3',
 'regex>=2022.1.18,<2023.0.0',
 'terminaltables>=3.1.0,<4.0.0']

entry_points = \
{'console_scripts': ['wizwalker = wizwalker.__main__:main']}

setup_kwargs = {
    'name': 'wizwalker',
    'version': '1.3.23',
    'description': 'Wizard101 scripting library',
    'long_description': "# WizWalker\n\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n\nWizard101 scripting library\n\n## documentation\nyou can find the documentation [here](https://starrfox.github.io/wizwalker/)\n\n## install\n```shell\n$ pip install -U wizwalker\n```\n\n## discord\njoin the offical discord [here](https://discord.gg/JHrdCNK)\n\n## development install\nThis package uses [poetry](https://python-poetry.org/)\n```shell\n$ poetry install\n```\n\n## running\nShell may need admin perms\n```shell\n$ poetry shell\n$ wizwalker\n```\n\n## building\nYou'll need the dev install (see above) for this to work\n\n### exe\n```shell\n# Admin if needed\n$ pyinstaller -F --uac-admin --name WizWalker wizwalker/__main__.py\n# Normal\n$ pyinstaller -F --name WizWalker wizwalker/__main__.py\n```\n\n### wheel and source\n```shell\n$ poetry build\n```\n\n### Docs\n```shell\n$ cd docs\n$ make html\n```\n\n## console commands\nwizwalker: Runs the wizwalker cli\n\nwizwalker start-wiz: start wizard101 instances\n\nwizwalker wad: edit and extract wizard101 wad files\n",
    'author': 'StarrFox',
    'author_email': 'starrfox6312@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/StarrFox/wizwalker',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
