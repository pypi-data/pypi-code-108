# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['foundry',
 'foundry.core',
 'foundry.core.player_animations',
 'foundry.core.sprites',
 'foundry.core.warnings',
 'foundry.game',
 'foundry.game.gfx',
 'foundry.game.gfx.drawable',
 'foundry.game.gfx.objects',
 'foundry.game.level',
 'foundry.gui',
 'foundry.smb3parse',
 'foundry.smb3parse.levels',
 'foundry.smb3parse.objects',
 'foundry.smb3parse.util']

package_data = \
{'': ['*'], 'foundry': ['data/*', 'data/icons/*']}

install_requires = \
['PySide6>=6.2.0,<7.0.0',
 'attrs>=21.2.0,<22.0.0',
 'pretty-errors>=1.2.24,<2.0.0',
 'pydantic>=1.8.2,<2.0.0',
 'qt-material>=2.8.13,<3.0.0',
 'single-source>=0.2.0,<0.3.0']

entry_points = \
{'console_scripts': ['foundry = foundry.main:start']}

setup_kwargs = {
    'name': 'foundry-smb3',
    'version': '0.4.11',
    'description': 'The future of SMB3',
    'long_description': '# Foundry\n\n<p align="center">\n<a href="https://github.com/TheJoeSmo/Foundry/actions"><img alt="Actions Status" src="https://github.com/TheJoeSmo/Foundry/actions/workflows/tests.yml/badge.svg"></a>\n<a href="https://github.com/TheJoeSmo/Foundry/actions"><img alt="Actions Status" src="https://github.com/TheJoeSmo/Foundry/actions/workflows/github_pages.yml/badge.svg"></a>\n<a href="https://github.com/TheJoeSmo/Foundry/block/main/LICENSE.md"><img alt="License GPL3" src="https://img.shields.io/badge/License-GPLv3-blue.svg"></a>\n<a href="https://pypi.org/project/foundry-smb3/"><img alt="PyPI" src="https://img.shields.io/pypi/v/foundry-smb3"></a>\n<a href="https://pepy.tech/project/black"><img alt="Downloads" src="https://pepy.tech/badge/foundry-smb3"></a>\n<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>\n</p>\n\nFoundry is the leading editor for SMB3.\n- Website: https://thejoesmo.github.io/Foundry/\n- Discord: https://discord.gg/pm87gm7\n- Documentation: https://thejoesmo.github.io/Foundry/\n- Manual: https://github.com/TheJoeSmo/Foundry/blob/master/MANUAL.md\n- Source Code: https://github.com/TheJoeSmo/Foundry\n- Bug Reporting: https://github.com/TheJoeSmo/Foundry/issues\n\nIt provides:\n- A powerful level editor\n\nTesting:\nFoundry uses `Poetry` as its package manager.  WIP.\n\nCall for Contributions\n----------------------\nFoundry is a community driven initiative that relies on your help and expertise.\n\nSmall improvements or fixes are critical to this repository\'s success.  Issues labeled `good first issue` are a great place to start.  For larger contributions WIP.\n\nYou do not need to be literate with programming to aid Foundry on its journey.  We also need help with:\n- Developing tutorials\n- Creating graphics for our brand and promotional material\n- Translation\n- Outreach and onboarding new contributors\n- Reviewing issues and suggestions\n\nIf you are undecided on where to start, we encourage you to reach out.  You can ask on our Discord or privately through email.\n\nIf you are new to open source projects and want to be caught up to speed, we recommend [this guide](https://opensource.guide/how-to-contribute/)',
    'author': 'TheJoeSmo',
    'author_email': 'joesmo.joesmo12@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9.0,<3.10',
}


setup(**setup_kwargs)
