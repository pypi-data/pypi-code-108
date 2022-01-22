# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['graia',
 'graia.ariadne',
 'graia.ariadne.console',
 'graia.ariadne.entry',
 'graia.ariadne.event',
 'graia.ariadne.message',
 'graia.ariadne.message.parser',
 'graia.ariadne.util']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.7.4,<4.0.0',
 'graia-broadcast>=0.14.4',
 'loguru>=0.5,<0.6',
 'prompt-toolkit>=3.0.24,<4.0.0',
 'pydantic>=1.8.2,<2.0.0',
 'regex>=2021.11.10,<2022.0.0',
 'typing-extensions>=4.0.0,<5.0.0',
 'yarl>=1.7,<2.0']

extras_require = \
{'alconna': ['arclet-alconna>=0.4.1,<0.5.0'],
 'document': ['mkdocs-material>=8.1.2', 'pdoc>=8.0,<9.0'],
 'full': ['arclet-alconna>=0.4.1,<0.5.0',
          'graia-scheduler>=0.0.6,<0.0.7',
          'graia-saya>=0.0.13,<0.0.14'],
 'graia': ['graia-scheduler>=0.0.6,<0.0.7', 'graia-saya>=0.0.13,<0.0.14']}

setup_kwargs = {
    'name': 'graia-ariadne',
    'version': '0.5.1rc4',
    'description': 'Another elegant framework for mirai and mirai-api-http v2.',
    'long_description': '<div align="center">\n\n# Ariadne\n\n_Another elegant framework for mirai and mirai-api-http v2._\n\n> 接受当下, 面向未来.\n\n<a href="https://pypi.org/project/graia-ariadne"><img alt="PyPI" src="https://img.shields.io/pypi/v/graia-ariadne" /></a></td>\n<a href="https://pypi.org/project/graia-ariadne"><img alt="PyPI Pre Release" src="https://img.shields.io/github/v/tag/GraiaProject/Ariadne?include_prereleases&label=latest&color=orange"></td>\n<a href="https://pypi.org/project/graia-ariadne"><img alt="Python Version" src="https://img.shields.io/pypi/pyversions/graia-ariadne" /></a>\n<a href="https://pypi.org/project/graia-ariadne"><img alt="Python Implementation" src="https://img.shields.io/pypi/implementation/graia-ariadne" /></a>\n\n<a href="https://graia.rtfd.io/"><img alt="docs" src="https://img.shields.io/badge/文档-click_here-black" /></a>\n<a href="https://graiaproject.github.io/Ariadne/"><img alt="API docs" src="https://img.shields.io/badge/API_文档-click_here-black"></a>\n<a href="https://github.com/psf/black"><img src="https://img.shields.io/badge/code%20style-black-black.svg" alt="black" /></a>\n<a href="https://pycqa.github.io/isort/"><img src="https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat" alt="isort"/></a>\n<a href="https://github.com/GraiaProject/Ariadne/blob/master/LICENSE"><img alt="License" src="https://img.shields.io/github/license/GraiaProject/Ariadne"></a>\n\n</div>\n\n**本项目适用于 mirai-api-http 2.0 以上版本**.\n\nAriadne 是 `Graia Project` 继承了 [`Application`](https://github.com/GraiaProject/Applicaiton) 并进行了许多改进后产生的作品,\n相信它可以给你带来良好的 `Python QQ Bot` 开发体验.\n\n**注意, 本框架需要 [`mirai-api-http v2`](https://github.com/project-mirai/mirai-api-http).**\n\n## 安装\n\n`poetry add graia-ariadne`\n\n或\n\n`pip install graia-ariadne`\n\n> 我们强烈建议使用 [`poetry`](https://python-poetry.org) 进行包管理\n\n## 开始使用\n\n```python\nfrom graia.ariadne.app import Ariadne\nfrom graia.ariadne.message.chain import MessageChain\nfrom graia.ariadne.message.element import Plain\nfrom graia.ariadne.model import Friend, MiraiSession\n\napp = Ariadne(MiraiSession(host="http://localhost:8080", verify_key="ServiceVerifyKey", account=123456789))\n\n\n@app.broadcast.receiver("FriendMessage")\nasync def friend_message_listener(app: Ariadne, friend: Friend):\n    await app.sendMessage(friend, MessageChain.create([Plain("Hello, World!")]))\n\n\napp.launch_blocking()\n```\n\n更多信息请看 [文档](https://graia.rtfd.io/).\n\n## 讨论\n\nQQ 交流群: [邀请链接](https://jq.qq.com/?_wv=1027&k=VXp6plBD)\n\n> QQ 群不定时清除不活跃成员, 请自行重新申请入群.\n\n## 文档\n\n[API 文档](https://graiaproject.github.io/Ariadne/) [官方文档](https://graia.rtfd.io/) [社区文档](https://graiax.cn)  [鸣谢](https://graia.rtfd.io/appendix/credits)\n\n**如果认为本项目有帮助, 欢迎点一个 `Star`.**\n\n## 协议\n\n本项目以[`GNU AGPLv3`](https://choosealicense.com/licenses/agpl-3.0/) 作为开源协议, 这意味着你需要遵守相应的规则.\n\n## 持续集成 (CI) 状态\n\n[![Dev PyPI Version](https://img.shields.io/pypi/v/graia-ariadne-dev?label=dev-pypi)](https://pypi.org/project/graia-ariadne-dev)\n[![Documentation Status](https://readthedocs.org/projects/graia/badge/?version=latest)](https://graia.rtfd.io/)\n\n\n[![Build and deploy API Docs](https://github.com/GraiaProject/Ariadne/actions/workflows/api_docs.yml/badge.svg)](https://github.com/GraiaProject/Ariadne/actions/workflows/api_docs.yml)\n[![Publish to PyPI](https://github.com/GraiaProject/Ariadne/actions/workflows/release-to-pypi.yml/badge.svg)](https://github.com/GraiaProject/Ariadne/actions/workflows/release-to-pypi.yml)\n## 开发版资源 / 参与开发\n\n[开发分支文档](https://graia-dev.rtfd.io/)\n[开发分支](https://github.com/GraiaProject/Ariadne/tree/dev)\n[开发版 PyPI](https://pypi.org/project/graia-ariadne-dev) \n[开始开发](./CONTRIBUTING.md)',
    'author': 'BlueGlassBlock',
    'author_email': 'blueglassblock@outlook.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://graia.rtfd.io/',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
