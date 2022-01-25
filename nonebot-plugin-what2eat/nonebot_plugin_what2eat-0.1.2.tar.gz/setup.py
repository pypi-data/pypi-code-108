# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nonebot_plugin_what2eat']

package_data = \
{'': ['*'], 'nonebot_plugin_what2eat': ['resource/*']}

install_requires = \
['ujson>=5.1.0,<6.0.0']

setup_kwargs = {
    'name': 'nonebot-plugin-what2eat',
    'version': '0.1.2',
    'description': 'What to eat today for your breakfast, lunch, dinner and even midnight snack!',
    'long_description': '<div align="center">\n\n# What to Eat\n\n<!-- prettier-ignore-start -->\n<!-- markdownlint-disable-next-line MD036 -->\n_🍔🌮🍜🍮🍣 今天吃什么 🍣🍮🍜🌮🍔_\n<!-- prettier-ignore-end -->\n\n</div>\n\n<p align="center">\n  \n  <a href="https://github.com/KafCoppelia/nonebot_plugin_what2eat/blob/main/LICENSE">\n    <img src="https://img.shields.io/badge/license-MIT-informational">\n  </a>\n  \n  <a href="https://github.com/nonebot/nonebot2">\n    <img src="https://img.shields.io/badge/nonebot2-2.0.0alpha.16-green">\n  </a>\n  \n  <a href="">\n    <img src="https://img.shields.io/badge/release-v0.1.2-orange">\n  </a>\n  \n</p>\n\n</p>\n\n## 版本\n\nv0.1.2\n\n⚠ 适配nonebot2-2.0.0alpha.16，适配beta.1版本参见[beta.1分支](https://github.com/KafCoppelia/nonebot_plugin_what2eat/tree/beta.1)\n\n## 安装\n\n1. 通过`pip`或`nb`安装版本，版本请指定`^0.1.2`；\n\n2. 数据默认位于`./resource/data.json`，可通过设置`env`下`WHAT2EAT_PATH`更改；基础菜单、群特色菜单及群友询问Bot次数会记录在该文件中；\n\n## 功能\n\n1. 选择恐惧症？让Bot给你今天吃什么建议！🍱\n\n2. 每餐每个时间段询问Bot建议上限可通过`EATING_LIMIT`修改（默认6次），每日6点、11点、17点、22点（夜宵）自动刷新；\n\n3. 群管理可自行添加或移除群特色菜单（`data.json`下`[group_food][group_id]`）；超管可添加或移除基础菜单（`[basic_food]`）；\n\n4. 各群特色菜单相互独立；各群每个时间段询问Bot建议次数独立；Bot会**综合各群特色菜单及基础菜单**给出建议；\n\n5. *TODO*：提醒按时吃饭小助手🤔，在做了在做了……\n\n## 命令\n\n1. 吃什么：今天吃什么、中午吃啥、今晚吃啥、中午吃什么、晚上吃啥、晚上吃什么、夜宵吃啥……\n\n2. [管理或群主或超管权限] 添加或移除：添加/移除 菜名；\n\n3. 查看菜单：查看菜单/群菜单；\n\n4. [仅超管权限] 加菜至基础菜单：加菜 菜名；\n\n## 注意\n\n尽量避免**基础菜单为空**情况，已在`./resource/data.json`内`[basic_food]`中写入几项。\n\n## 本插件改自：\n\n[HoshinoBot-whattoeat](https://github.com/pcrbot/whattoeat)',
    'author': 'KafCoppelia',
    'author_email': 'k740677208@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.3,<4.0.0',
}


setup(**setup_kwargs)
