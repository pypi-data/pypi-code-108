# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nonebot_plugin_help']

package_data = \
{'': ['*']}

install_requires = \
['nonebot-adapter-cqhttp<=2.0.0a16', 'nonebot2<=2.0.0.a16']

setup_kwargs = {
    'name': 'nonebot-plugin-help',
    'version': '0.1.6',
    'description': 'A general help lister for nonebot2 plugins',
    'long_description': '<div align="center">\n\n# nonebot-plugin-help\n### Nonebot2 轻量级帮助插件\n\n<a href="https://raw.githubusercontent.com/xzhouqd/nonebot-plugin-help/main/LICENSE">\n    <img src="https://img.shields.io/github/license/xzhouqd/nonebot-plugin-help?style=for-the-badge" alt="license">\n</a>\n<a href="https://pypi.python.org/pypi/nonebot-plugin-help">\n    <img src="https://img.shields.io/pypi/v/nonebot-plugin-help?color=green&style=for-the-badge" alt="pypi">\n</a>\n<img src="https://img.shields.io/badge/python-3.7.3+-blue?style=for-the-badge" alt="python">\n<br />\n<img src="https://img.shields.io/badge/tested_python-3.8.9-blue?style=for-the-badge" alt="python">\n<img src="https://img.shields.io/static/v1?label=tested+env&message=go-cqhttp+1.0.0-beta8-fix1&color=blue&style=for-the-badge" alt="python">\n\n<br />\n<a href="https://github.com/botuniverse/onebot/blob/master/README.md">\n    <img src="https://img.shields.io/badge/Onebot-v11-brightgreen?style=for-the-badge" alt="onebot">\n</a>\n<a href="https://github.com/nonebot/nonebot2">\n    <img src="https://img.shields.io/badge/Nonebot-2.0.0a16-red?style=for-the-badge" alt="nonebot">\n</a>\n<a href="https://pypi.org/project/nonebot-adapter-cqhttp/">\n    <img src="https://img.shields.io/static/v1?label=Nonebot-adapters-cqhttp&message=2.0.0a16&color=red&style=for-the-badge" alt="nonebot-adapters-cqhttp">\n</a>\n</div>\n\n## 开发者接入此插件列表方法\n### 包级别接入\n使用python包形态的插件（已发布/自行开发皆可），并在插件包的__init__.py文件内增加如下代码：\n```python\n# 若此文本不存在，将显示包的__doc__\n__usage__ = \'您想在使用命令/help <your plugin package name>时提供的帮助文本\'\n\n# 您的插件版本号，将在/help list中显示\n__help__version__ = \'0.1.6\' \n\n# 此名称有助于美化您的插件在/help list中的显示\n# 但使用/help xxx查询插件用途时仍必须使用包名\n__help__plugin_name__ = "您的插件名称（有别于nonebot-plugin-xxx的包名）" \n```\n### Matcher级别接入\nMatcher级别帮助请为Matcher添加如下代码：\n```python\ndefault_start = list(nonebot.get_driver().config.command_start)[0]\nhelper = on_command("help", priority=1, aliases={"帮助"})\nhelper.__help_name__ = \'您的命令触发指令名\'\nhelper.__help_info__ = f\'您为此命令提供的帮助文本\'\nhelper.__doc__ = f\'您为此命令提供的帮助文本, 当您不希望使用__help_info__提供时，可以使用__doc__提供\'\n```\n请注意：当您未提供`__help_name__`或`__help_info__`与`__doc__`中的一个时，此Matcher不会列入Matcher级别帮助！\n\n## 实际使用\n此部分介绍以使用\'/\'作为command_start为例。\n### 获取本插件帮助\n指令： /help\n\n返回示例：\n```\n@<user_who_send_command> 欢迎使用Nonebot 2 Help Plugin\n支持使用的前缀：/\n/help  # 获取本插件帮助\n/help list  # 展示已加载插件列表\n/help <plugin_name>  # 调取目标插件帮助信息\n```\n### 查看已加载插件列表\n指令：/help list\n\n返回示例：\n```\n@<user_who_send_command> 已加载插件：\nnonebot.plugins.echo \nnonebot_guild_patch \nnonebot_plugin_cloverdata | 四叶草魔物娘属性计算插件 0.1.0\nnonebot_plugin_help | XZhouQD\'s Help Menu 0.1.5\n```\n\n### 查看已加载某一插件用途\n指令：/help <plugin_package_name>\n示例：\n```\n/help nonebot_plugin_help\n\n@<user_who_send_command> 欢迎使用Nonebot 2 Help Plugin\n本插件提供公共帮助菜单能力\n此Bot配置的命令前缀：/\n\n\n序号. 命令名: 命令用途\n1. help: /help  # 获取本插件帮助\n/help list  # 展示已加载插件列表\n/help <plugin_name>  # 调取目标插件帮助信息\n```\n\n若插件未提供__usage__，则会显示__doc__，示例：\n```\n/help nonebot_plugin_help\n\n@<user_who_send_command>\nNonebot 2 Help Plugin\nAuthor: XZhouQD\nSince: 16 May 2021\n\n\n序号. 命令名: 命令用途\n1. help: /help  # 获取本插件帮助\n/help list  # 展示已加载插件列表\n/help <plugin_name>  # 调取目标插件帮助信息\n```',
    'author': 'XZhouQD',
    'author_email': 'X.Zhou.QD@hotmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/XZhouQD/nonebot-plugin-help',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.3,<4.0.0',
}


setup(**setup_kwargs)
