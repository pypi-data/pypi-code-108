# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nonebot_plugin_analysis_bilibili']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.7,<4.0', 'nonebot2>=2.0.0a16,<3.0.0']

setup_kwargs = {
    'name': 'nonebot-plugin-analysis-bilibili',
    'version': '2.2.5',
    'description': 'nonebot2解析bilibili插件',
    'long_description': '<!--\n * @Author         : mengshouer\n * @Date           : 2021-03-16 00:00:00\n * @LastEditors    : mengshouer\n * @LastEditTime   : 2021-03-16 00:00:00\n * @Description    : None\n * @GitHub         : https://github.com/mengshouer/nonebot_plugin_analysis_bilibili\n-->\n\n<p align="center">\n  <a href="https://v2.nonebot.dev/"><img src="https://v2.nonebot.dev/logo.png" width="200" height="200" alt="nonebot"></a>\n</p>\n\n<div align="center">\n\n# nonebot_plugin_analysis_bilibili\n\n\n_✨ NoneBot bilibili视频、番剧解析插件 ✨_\n\n</div>\n\n<p align="center">\n  <a href="https://raw.githubusercontent.com/cscs181/QQ-Github-Bot/master/LICENSE">\n    <img src="https://img.shields.io/github/license/cscs181/QQ-Github-Bot.svg" alt="license">\n  </a>\n  <a href="https://pypi.python.org/pypi/nonebot-plugin-analysis-bilibili">\n    <img src="https://img.shields.io/pypi/v/nonebot-plugin-analysis-bilibili.svg" alt="pypi">\n  </a>\n  <img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="python">\n</p>\n\n## 使用方式\n私聊或群聊发送bilibili的小程序/链接\n\n## 安装\npip install nonebot_plugin_analysis_bilibili\n\n```\npip install --upgrade nonebot_plugin_analysis_bilibili\n```\n在 Nonebot2 入口文件（例如 bot.py ）增加：\n``` python\nnonebot.load_plugin("nonebot_plugin_analysis_bilibili")\n```\n',
    'author': 'mengshouer',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/mengshouer/nonebot_plugin_analysis_bilibili',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
