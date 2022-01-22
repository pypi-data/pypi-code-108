# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nonebot_plugin_manager']

package_data = \
{'': ['*']}

install_requires = \
['httpx>=0.21.3,<0.22.0',
 'nonebot-adapter-onebot>=2.0.0-beta.1,<3.0.0',
 'nonebot2>=2.0.0-beta.1,<3.0.0']

setup_kwargs = {
    'name': 'nonebot-plugin-manager',
    'version': '0.5.8',
    'description': 'Nonebot Plugin Manager base on import hook',
    'long_description': '<div align="center">\n\t<img width="200" src="docs/logo.png" alt="logo"></br>\n\n# Nonebot Plugin Manager\n\n基于 [nonebot2](https://github.com/nonebot/nonebot2) 和 [go-cqhttp](https://github.com/Mrs4s/go-cqhttp) 的**非侵入式**插件管理器\n\n[![License](https://img.shields.io/github/license/Jigsaw111/nonebot_plugin_manager)](LICENSE)\n![Python Version](https://img.shields.io/badge/python-3.7.3+-blue.svg)\n![NoneBot Version](https://img.shields.io/badge/nonebot-2.0.0a11+-red.svg)\n![Pypi Version](https://img.shields.io/pypi/v/nonebot-plugin-manager.svg)\n\n</div>\n\n## 安装\n\n**插件仍在~~快速~~开发中，遇到问题还请务必提 issue。**\n\n### 从 PyPI 安装（推荐）\n\n- 使用 nb-cli  \n\n```bash\nnb plugin install nonebot_plugin_manager\n```\n\n- 使用 poetry\n\n```bash\npoetry add nonebot_plugin_manager\n```\n\n- 使用 pip\n\n```bash\npip install nonebot_plugin_manager\n```\n\n### 从 GitHub 安装（不推荐）\n\n```bash\ngit clone https://github.com/Jigsaw111/nonebot_plugin_manager.git\n```\n\n## 使用\n\n### 权限\n\n权限与 UNIX 的权限类似，分为三种用户：超级用户、用户、群。\n\n每种用户包含读、写、执行 3 个权限，分别对应数字 4、2、1，将 3 个权限对应的数字累加，最终得到的值即可作为每种用户所具有的权限。\n\n关于会话中使用什么模式，可参照下表：\n\n| 仅供参考 | 私聊读   | 群聊读 | 私聊写   | 群聊写    | 私聊执行 | 群聊执行  |\n| -------- | -------- | ------ | -------- | --------- | -------- | --------- |\n| 超级用户 | 超级用户 | 群     | 超级用户 | 超级用户  | 超级用户 | 群        |\n| 用户     | 用户     | 群     | 用户     | 无权限    | 用户     | 用户 & 群 |\n| 群管理员 | 不存在   | 群     | 不存在   | 用户 & 群 | 不存在   | 用户 & 群 |\n\n包含 Matcher 的插件默认权限为`755`，不含 Matcher 的插件默认权限为`311`。\n\n> 例：`npm chmod nonebot_plugin_nodice 757`命令可将 nonebot_plugin_nodice 的权限设置为`757`\n> 即超级用户可写可读可执行，用户可读可执行，群可写可读可执行。\n\n只有超级用户可以修改插件的权限，可以使用绝对模式（八进制数字模式）~~，符号模式~~指定文件的权限。\n\n### 命令\n\n**使用前请先确保命令前缀为空，否则请在以下命令前加上命令前缀 (默认为`/`)。**\n\n- `npm ls`查看当前会话插件列表\n- - `-s, --store`互斥参数，查看插件商店列表（仅超级用户可用）\n- - `-u user_id, --user user_id`互斥参数，查看指定用户插件列表（仅超级用户可用）\n- - `-g group_id, --group group_id`互斥参数，查看指定群插件列表（仅超级用户可用）\n- - `-a, --all`可选参数，查看所有插件（包括不含 Matcher 的插件）\n\n- `npm info 插件名`查询插件信息 （仅超级用户可用）\n\n- `npm chmod mode plugin ...`设置插件权限（仅超级用户可用）\n- - `mode`必选参数，需要设置的权限，参考上文\n- - `plugin...`必选参数，需要设置的插件名\n- - `-a, --all`可选参数，全选插件\n- - `-r, --reverse`可选参数，反选插件\n\n- `npm block plugin...`禁用当前会话插件（需要权限）\n- - `plugin...`必选参数，需要禁用的插件名\n- - `-a, --all`可选参数，全选插件\n- - `-r, --reverse`可选参数，反选插件\n- - `-u user_id ..., --user user_id ...`可选参数，管理指定用户设置（仅超级用户可用）\n- - `-g group_id ..., --group group_id ...`可选参数，管理指定群设置（仅超级用户可用）\n\n- `npm unblock plugin...`启用当前会话插件（需要权限）\n- - `plugin...`必选参数，需要禁用的插件名\n- - `-a, --all`可选参数，全选插件\n- - `-r, --reverse`可选参数，反选插件\n- - `-u user_id ..., --user user_id ...`可选参数，管理指定用户设置（仅超级用户可用）\n- - `-g group_id ..., --group group_id ...`可选参数，管理指定群设置（仅超级用户可用）\n\n<!-- TODO\n\n- `npm install plugin...`安装插件（仅超级用户可用）\n- - `-i index, --index index`指定 PyPI 源\n\n- `npm uninstall plugin...`卸载插件（仅超级用户可用）\n- - `-a, --all`可选参数，全选插件\n\n-->\n\n### 导入\n\n`PluginManager`是封装好的插件管理器类，导入后可以直接使用。\n\n```python\nfrom nonebot_plugin_manager import PluginManager\n```\n\n## Q&A\n\n- **这是什么？**  \n  基于 import hook 的插件管理器，能够在不重启 NoneBot2 的情况下分群管理插件。\n- **有什么用？**  \n  在 NoneBot2 仍然缺乏插件管理机制的时期暂时充当插件管理器。\n- **自造 Rule 不是更好？**  \n  Rule 当然更好且更有效率，但是 Rule 是一种**侵入式**的插件管理方式，需要用户自行修改其他插件的源码，这对于管理从 PyPI 安装的插件来说相对复杂。而使用本插件，你不需要修改其他插件的任何内容，更符合插件之间**松耦合**的设计原则。\n\n<details>\n<summary>展开更多</summary>\n\n## 原理\n\n使用`run_preprocessor`装饰器，在 Matcher 运行之前检测其所属的 Plugin 判断是否打断。\n\n事实上 Nonebot 还是加载了插件，所以只能算是**屏蔽**而非**卸载**。\n\n<!-- TODO\n\n当然，你也可以使用`npm uninstall`命令来真正卸载插件，但我不建议你这样做，因为该命令将会重启 Nonebot 。\n\n-->\n\n## To Do\n\n- [x] 分群插件管理\n- [ ] 完善权限系统\n- [ ] 设置插件别名\n\n*咕咕咕*\n\n- [ ] 安装卸载插件\n\n## Bug\n\n- [ ] 无法停用 Matcher 以外的机器人行为（如 APScheduler ）  \n  **解决方法：** 暂无\n- [x] 任何人都可以屏蔽/启用插件\n- [x] 如果加载了内置插件将会导致错误\n\n</details>\n',
    'author': 'Jigsaw',
    'author_email': 'j1g5aw@foxmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/Jigsaw111/nonebot_plugin_manager',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.3,<4.0.0',
}


setup(**setup_kwargs)
