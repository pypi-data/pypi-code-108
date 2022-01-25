# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cyan', 'cyan.event', 'cyan.model', 'cyan.model.message', 'cyan.util']

package_data = \
{'': ['*']}

install_requires = \
['frozendict>=2.2.0,<3.0.0', 'httpx>=0.21.1,<0.22.0', 'websockets>=10.1,<11.0']

setup_kwargs = {
    'name': 'cyanidebot',
    'version': '0.2.1',
    'description': 'A Python SDK for QQ Bot.',
    'long_description': '<div align="center">\n    <img src="logo.png" width="200" alt="cyan">\n</div>\n\n<div align="center">\n\n[![Pipeline Status](https://gitlab.huajitech.net/worldmozara/cyanide/badges/main/pipeline.svg)](https://gitlab.huajitech.net/worldmozara/cyanide/-/commits/main)\n[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)](https://gitlab.huajitech.net/worldmozara/cyanide)\n[![PyPI - License](https://img.shields.io/pypi/l/cyanidebot)](https://gitlab.huajitech.net/worldmozara/cyanide)\n[![PyPI](https://img.shields.io/pypi/v/cyanidebot)](https://gitlab.huajitech.net/worldmozara/cyanide)\n[![PyPI - Downloads](https://img.shields.io/pypi/dm/cyanidebot)](https://pypi.org/project/cyanidebot/)\n\n</div>\n\n---\n\n## 简介\n\nCyanide 是一个适用于 Python 3.9+ 的简单易用的 QQ 机器人 SDK，基于 Python 的类型注解和异步特性。\n\n该项目 fork 自 [Cyan](https://gitlab.huajitech.net/huajitech/cyan)。\n\n## 项目状态\n\n项目目前处于测试阶段，这意味着 SDK 所提供的操作不稳定，不建议用于生产环境。\n\n## 仓库\n\nHuajiTech GitLab（主仓库）：\n- Cyanide: https://gitlab.huajitech.net/worldmozara/cyanide\n- Cyan: https://gitlab.huajitech.net/huajitech/cyan\n\nGitHub：\n- Cyanide: https://github.com/NCBM/Cyanide\n- Cyan: https://github.com/huajitech/cyan\n\n## 特性\n\n- 异步操作：使用 `httpx`、`websockets` 异步框架及 Python 的异步特性\n- 化繁为简：简化 API 繁琐的操作，使用户容易上手\n- 类型注释：SDK 100% 使用类型注解，通过 `Pyright` 的**严格**检查，用户可使用支持类型检查的 IDE 减少 Bug 出现的可能性\n- 支持扩展：SDK 开放与 API 交互的函数，用户可通过提供的函数与 API 交互，实现 SDK 未实现的功能\n\n## 如何使用\n\n### 安装\n\n1. 通过 `pip` 安装 Cyanide (release)：\n    ```bash\n    pip install cyansdk\n    ```\n\n2. Cyanide (daily)：(WIP)\n\n### 文档\n\nhttps://huajitech.proj.zone/cyan\n\n## 示例\n\n```py\nfrom cyan import Session, Ticket\nfrom cyan.event import ChannelMessageReceivedEvent\nfrom cyan.model import Message\n\nsession = Session(\n    "https://sandbox.api.sgroup.qq.com/",\n    Ticket("{app_id}", "{token}")\n)\n\n\n@session.on(ChannelMessageReceivedEvent)\nasync def message_received(data: Message):\n    await data.reply("收到消息：\\n", data)\n\nsession.run()\n```\n\n[更多](examples)\n',
    'author': 'Ricky8955555',
    'author_email': '397050061@qq.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.huajitech.net/worldmozara/cyanide',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
