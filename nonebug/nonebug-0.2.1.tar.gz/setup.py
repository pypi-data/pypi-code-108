# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nonebug', 'nonebug.mixin', 'nonebug.mixin.call_api', 'nonebug.mixin.process']

package_data = \
{'': ['*']}

install_requires = \
['asgiref>=3.4.0,<4.0.0',
 'async-asgi-testclient>=1.4.8,<2.0.0',
 'nonebot2>=2.0.0-beta.1,<3.0.0',
 'pytest-asyncio>=0.16.0,<0.17.0',
 'pytest>=6.2.5,<7.0.0',
 'typing-extensions>=4.0.0,<5.0.0']

entry_points = \
{'pytest11': ['nonebug = nonebug.fixture']}

setup_kwargs = {
    'name': 'nonebug',
    'version': '0.2.1',
    'description': 'nonebot2 test framework',
    'long_description': '<!-- markdownlint-disable MD033 MD041 -->\n\n<p align="center">\n  <a href="https://v2.nonebot.dev/"><img src="https://v2.nonebot.dev/logo.png" width="200" height="200" alt="nonebot"></a>\n</p>\n\n<div align="center">\n\n# NoneBug\n\n<!-- prettier-ignore-start -->\n<!-- markdownlint-disable-next-line MD036 -->\n_✨ NoneBot2 测试框架 ✨_\n<!-- prettier-ignore-end -->\n\n</div>\n\n<p align="center">\n  <a href="https://raw.githubusercontent.com/nonebot/nonebug/master/LICENSE">\n    <img src="https://img.shields.io/github/license/nonebot/nonebug" alt="license">\n  </a>\n  <a href="https://pypi.python.org/pypi/nonebug">\n    <img src="https://img.shields.io/pypi/v/nonebug" alt="pypi">\n  </a>\n  <img src="https://img.shields.io/badge/python-3.7.3+-blue" alt="python">\n  <a href="https://codecov.io/gh/nonebot/nonebug">\n    <img src="https://codecov.io/gh/nonebot/nonebug/branch/master/graph/badge.svg?token=LDK2OFR231"/>\n  </a>\n  <br />\n  <a href="https://jq.qq.com/?_wv=1027&k=5OFifDh">\n    <img src="https://img.shields.io/badge/qq%E7%BE%A4-768887710-orange?style=flat-square" alt="QQ Chat">\n  </a>\n  <a href="https://t.me/botuniverse">\n    <img src="https://img.shields.io/badge/telegram-botuniverse-blue?style=flat-square" alt="Telegram Channel">\n  </a>\n  <a href="https://discord.gg/VKtE6Gdc4h">\n    <img src="https://discordapp.com/api/guilds/847819937858584596/widget.png?style=shield" alt="Discord Server">\n  </a>\n</p>\n',
    'author': 'AkiraXie',
    'author_email': 'l997460364@outlook.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://v2.nonebot.dev/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7.3,<4.0.0',
}


setup(**setup_kwargs)
