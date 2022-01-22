# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nonebot_plugin_what2eat']

package_data = \
{'': ['*'], 'nonebot_plugin_what2eat': ['resource/*']}

setup_kwargs = {
    'name': 'nonebot-plugin-what2eat',
    'version': '0.1.0',
    'description': 'What to eat today for your breakfast, lunch, dinner and even midnight snack!',
    'long_description': '<div align="center">\n\n# What to Eat\n\n<!-- prettier-ignore-start -->\n<!-- markdownlint-disable-next-line MD036 -->\n_🍔 今天吃什么 🍔_\n<!-- prettier-ignore-end -->\n\n</div>\n\n<p align="center">\n  \n  <a href="https://github.com/KafCoppelia/nonebot_plugin_what2eat/blob/main/LICENSE">\n    <img src="https://img.shields.io/badge/license-MIT-informational">\n  </a>\n  \n  <a href="https://github.com/nonebot/nonebot2">\n    <img src="https://img.shields.io/badge/nonebot2-2.0.0alpha.16-green">\n  </a>\n  \n  <a href="">\n    <img src="https://img.shields.io/badge/release-v0.1.0-orange">\n  </a>\n  \n</p>\n\n</p>\n\n## 版本\n\nv0.1.0\n\n⚠ 适配nonebot2-2.0.0alpha.16！\n\n## 安装\n\n1. 通过`pip`或`poetry`安装；\n\n2. 菜单及群友吃什么的数据默认位于`./resource/data.json`，可通过设置`env`下`WHAT2EAT_PATH`更改；群友询问Bot的次数会记录在该文件中；\n\n## 功能\n\n1. 选择恐惧症？让Bot给三餐你吃什么建议；\n\n2. 每餐Bot提出建议上限可通过`EATING_LIMIT`修改（默认5次），每日6点、11点、17点自动刷新次数；\n\n3. 群友可自行添加或移除菜品，或许需要加权限限制🤔；\n\n## 命令\n\n1. 吃什么：今天吃什么、中午吃啥、今晚吃啥、中午吃什么、晚上吃啥、晚上吃什么……\n\n2. 添加或移除：添加/移除 菜名；\n\n## 本插件改自：\n\n[HoshinoBot-whattoeat](https://github.com/pcrbot/whattoeat)',
    'author': 'KafCoppelia',
    'author_email': 'k740677208@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7.3,<4.0.0',
}


setup(**setup_kwargs)
