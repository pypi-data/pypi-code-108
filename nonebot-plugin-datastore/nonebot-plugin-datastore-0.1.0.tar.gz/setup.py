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
    'version': '0.1.0',
    'description': '适用于 Nonebot2 的数据存储插件',
    'long_description': '<!-- markdownlint-disable MD033 MD036 MD041 -->\n\n<p align="center">\n  <a href="https://v2.nonebot.dev/"><img src="https://v2.nonebot.dev/logo.png" width="200" height="200" alt="nonebot"></a>\n</p>\n\n<div align="center">\n\n# NoneBot Plugin DataStore\n\n_✨ NoneBot 数据存储插件 ✨_\n\n</div>\n\n<p align="center">\n  <a href="https://raw.githubusercontent.com/he0119/nonebot-plugin-datastore/master/LICENSE">\n    <img src="https://img.shields.io/github/license/he0119/nonebot-plugin-datastore.svg" alt="license">\n  </a>\n  <a href="https://pypi.python.org/pypi/nonebot-plugin-datastore">\n    <img src="https://img.shields.io/pypi/v/nonebot-plugin-datastore.svg" alt="pypi">\n  </a>\n  <img src="https://img.shields.io/badge/python-3.7.3+-blue.svg" alt="python">\n</p>\n\n## 使用方式\n\n加载插件后直接导出方法\n\n```python\nfrom nonebot.params import Depends\nfrom nonebot_plugin_localstore import PluginData, get_session\nfrom sqlmodel.ext.asyncio.session import AsyncSession\n\nDATA = PluginData("plugin_name")\n\n@matcher.handle()\ndef handle(session: AsyncSession = Depends(get_session)):\n    await session.exec()\n```\n\n## 配置项\n\n配置方式：直接在 `NoneBot` 全局配置文件中添加以下配置项即可。\n\n### datastore_cache_dir\n\n- 类型: `str`\n- 默认: [nonebot_plugin_localstore](https://github.com/nonebot/plugin-localstore) 插件提供的缓存目录\n- 说明: 缓存目录\n\n### datastore_config_dir\n\n- 类型: `str`\n- 默认: [nonebot_plugin_localstore](https://github.com/nonebot/plugin-localstore) 插件提供的配置目录\n- 说明: 配置目录\n\n### datastore_data_dir\n\n- 类型: `str`\n- 默认: [nonebot_plugin_localstore](https://github.com/nonebot/plugin-localstore) 插件提供的数据目录\n- 说明: 数据目录\n\n### datastore_enable_database\n\n- 类型: `bool`\n- 默认: `False`\n- 说明: 是否启动数据库\n\n### datastore_database_url\n\n- 类型: `str`\n- 默认: `sqlite+aiosqlite:///data_dir/data.db`\n- 说明: 数据库连接字符串，默认使用 SQLite 数据库\n\n### datastore_database_echo\n\n- 类型: `bool`\n- 默认: `False`\n- 说明: 是否显示数据库执行的语句与其参数列表\n\n## 计划\n\n- [x] 调整配置为 K-V 存储\n- [x] 调整配置存放位置至专门的配置目录\n- [x] 数据库为可选项\n- [ ] 支持将配置存放至数据库中\n- [ ] 支持 Alembic\n',
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
