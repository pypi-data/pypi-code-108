# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nonebot_plugin_datastore']

package_data = \
{'': ['*']}

install_requires = \
['aiosqlite>=0.17.0,<0.18.0',
 'nonebot-plugin-localstore>=0.1.0,<0.2.0',
 'nonebot2[httpx]>=2.0.0-beta.1,<3.0.0',
 'sqlmodel>=0.0.6,<0.0.7']

setup_kwargs = {
    'name': 'nonebot-plugin-datastore',
    'version': '0.0.2',
    'description': '适用于 Nonebot2 的数据存储插件',
    'long_description': '<!-- markdownlint-disable MD033 MD036 MD041 -->\n\n<p align="center">\n  <a href="https://v2.nonebot.dev/"><img src="https://v2.nonebot.dev/logo.png" width="200" height="200" alt="nonebot"></a>\n</p>\n\n<div align="center">\n\n# nonebot-plugin-datastore\n\n_✨ NoneBot 数据存储插件 ✨_\n\n</div>\n\n<p align="center">\n  <a href="https://raw.githubusercontent.com/he0119/nonebot-plugin-datastore/master/LICENSE">\n    <img src="https://img.shields.io/github/license/he0119/nonebot-plugin-datastore.svg" alt="license">\n  </a>\n  <a href="https://pypi.python.org/pypi/nonebot-plugin-datastore">\n    <img src="https://img.shields.io/pypi/v/nonebot-plugin-datastore.svg" alt="pypi">\n  </a>\n  <img src="https://img.shields.io/badge/python-3.7.3+-blue.svg" alt="python">\n</p>\n\n## 使用方式\n\n~待会儿写~\n\n## 配置项\n\n配置方式：直接在 NoneBot 全局配置文件中添加以下配置项即可。\n\n### cache_dir\n\n- 类型: `str`\n- 默认: [nonebot_plugin_localstore](https://github.com/nonebot/plugin-localstore) 插件提供的缓存目录\n- 说明: 缓存目录\n\n### config_dir\n\n- 类型: `str`\n- 默认: [nonebot_plugin_localstore](https://github.com/nonebot/plugin-localstore) 插件提供的配置目录\n- 说明: 配置目录\n\n### data_dir\n\n- 类型: `str`\n- 默认: [nonebot_plugin_localstore](https://github.com/nonebot/plugin-localstore) 插件提供的数据目录\n- 说明: 数据目录\n\n### database_url\n\n- 类型: `str`\n- 默认: `sqlite+aiosqlite:///data_dir/data.db`\n- 说明: 数据库连接字符串\n',
    'author': 'hemengyang',
    'author_email': 'hmy0119@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/he0119/nonebot-plugin-datastore',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.3,<4.0.0',
}


setup(**setup_kwargs)
