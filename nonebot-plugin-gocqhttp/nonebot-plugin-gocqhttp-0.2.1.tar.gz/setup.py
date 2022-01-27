# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nonebot_plugin_gocqhttp',
 'nonebot_plugin_gocqhttp.process',
 'nonebot_plugin_gocqhttp.process.device',
 'nonebot_plugin_gocqhttp.web']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0',
 'httpx[http2]>=0.21.3,<0.22.0',
 'nonebot-adapter-onebot>=2.0.0-beta.1,<3.0.0',
 'nonebot2>=2.0.0-beta.1,<3.0.0',
 'psutil>=5.9.0,<6.0.0']

setup_kwargs = {
    'name': 'nonebot-plugin-gocqhttp',
    'version': '0.2.1',
    'description': 'A plugin to run go-cqhttp directly in NoneBot2, without additional download and installation.',
    'long_description': '# nonebot-plugin-gocqhttp\n\n> *A plugin to run go-cqhttp directly in NoneBot2, without additional download and installation.*\n\n> **一款在NoneBot2中直接运行go-cqhttp的插件, 无需额外下载安装.**\n\n![PyPI](https://img.shields.io/pypi/v/nonebot-plugin-gocqhttp?style=for-the-badge)\n\n[![GitHub issues](https://img.shields.io/github/issues/mnixry/nonebot-plugin-gocqhttp)](https://github.com/mnixry/nonebot-plugin-gocqhttp/issues)\n[![GitHub forks](https://img.shields.io/github/forks/mnixry/nonebot-plugin-gocqhttp)](https://github.com/mnixry/nonebot-plugin-gocqhttp/network)\n[![GitHub stars](https://img.shields.io/github/stars/mnixry/nonebot-plugin-gocqhttp)](https://github.com/mnixry/nonebot-plugin-gocqhttp/stargazers)\n[![GitHub license](https://img.shields.io/github/license/mnixry/nonebot-plugin-gocqhttp)](https://github.com/mnixry/nonebot-plugin-gocqhttp/blob/main/LICENSE)\n\n## 为什么?\n\n- ~~为了对标[`koishijs/koishi-plugin-gocqhttp`](https://github.com/koishijs/koishi-plugin-gocqhttp/)~~\n\n- 为了不用同时手动启动`go-cqhttp`和`nonebot`进程, 非常方便\n\n- 为了便于Docker等进行部署, 只需制作一个`nonebot`容器即可\n\n## 怎么用?\n\n### 安装\n\n推荐使用`nb-cli`进行安装\n<!--TODO: add a tutorial link to guide user installation-->\n\n### 配置\n\n本项目提供以下配置项, 请在`.env`中自行进行配置\n\n如果想要获取更多配置文件相关信息, 请[阅读源代码](./nonebot_plugin_gocqhttp/plugin_config.py)\n\n- `ACCOUNTS`: 要登录的QQ账号列表, 为一个json数组\n\n  - 支持的字段:\n    - `uin`: QQ账号 **(必填)**\n    - `password`: QQ密码, 不填将使用扫码登录\n    - `protocol`: 数字, 是登录使用的[客户端协议](https://docs.go-cqhttp.org/guide/config.html#%E8%AE%BE%E5%A4%87%E4%BF%A1%E6%81%AF)\n    - `config_extra`: 配置文件拓展, 用于覆盖默认配置\n      - 由于在每次程序启动时`go-cqhttp`启动配置文件都会被覆盖, 所以请在该项目中设置你要添加的配置项\n        - 当直接填写json对象时, 原样传入并更新配置文件\n        - 当传入以`ref:`开头的字符串时, 它将尝试读取之后目录中的文件, 来更改配置文件\n        - 当传入以`override:`开头的字符串时, 它将尝试尝试读取之后目录中的文件, 来覆盖配置文件\n    - `device_extra`: 和`config_extra`类似, 但是是用来覆盖`device.json`中配置的\n\n  - 示例:\n\n    ```json\n        [\n            {\n                "uin":"QQ帐号",\n                "password":"密码",\n            }\n        ]\n    ```\n\n- `DOWNLOAD_REPO`: 要下载的仓库, 默认为[`Mrs4s/gocqhttp`](https://github.com/Mrs4s/go-cqhttp/)\n- `DOWNLOAD_VERSION`: 要下载的版本, 默认为`latest`, 即最新版本\n- `DOWNLOAD_URL`: 下载URL, 支持多个占位符\n- `FORCE_DOWNLOAD`: 强制在启动时下载, 默认为`false`\n- `PROCESS_RESTARTS`: 尝试重启进程的次数, 小于0则不限制, 默认为`-1`\n\n### 使用\n\n配置好了以后启动你的Bot即可\n\n- **需要注意以下几点**:\n  - 本插件会在工作目录下创建`accounts`文件夹用于存储`go-cqhttp`的二进制和数据文件, 如果你使用版本管理工具(如`git`), 请自行将该文件夹加入[忽略列表](./.gitignore)\n  - 本插件通过子进程调用实现, 如果你在外部终止了Bot进程, 请检查开启的子进程是否也同样已终止\n\n本插件提供了一个[仅`SUPERUSERS`能用的命令](./nonebot_plugin_gocqhttp/plugin.py): `gocq`, 可以用来查看当前运行的`go-cqhttp`进程状态\n\n## 鸣谢\n\n- [`koishijs/koishi-plugin-gocqhttp`](https://github.com/koishijs/koishi-plugin-gocqhttp/): 本项目直接参考 ~~(直接开抄)~~\n- [`Mrs4s/gocqhttp`](https://github.com/Mrs4s/go-cqhttp/), [`nonebot/nonebot2`](https://github.com/nonebot/nonebot2): ~~(看看项目名, 什么成分不用多说了吧)~~ 本项目的套壳的核心\n\n## 开源许可证\n\n由于`go-cqhttp`使用了[AGPL-3.0](https://github.com/Mrs4s/go-cqhttp/blob/master/LICENSE)许可证, 本项目也同样使用该许可\n\n**注意! 如果在您的项目中使用了该插件, 您的项目也同样以该许可开源!**\n\n    A plugin to run go-cqhttp directly in NoneBot2, without additional download and installation.\n    Copyright (C) 2022 Mix\n\n    This program is free software: you can redistribute it and/or modify\n    it under the terms of the GNU Affero General Public License as published\n    by the Free Software Foundation, either version 3 of the License, or\n    (at your option) any later version.\n\n    This program is distributed in the hope that it will be useful,\n    but WITHOUT ANY WARRANTY; without even the implied warranty of\n    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the\n    GNU Affero General Public License for more details.\n\n    You should have received a copy of the GNU Affero General Public License\n    along with this program.  If not, see <https://www.gnu.org/licenses/>.\n',
    'author': 'Mix',
    'author_email': 'mnixry@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/mnixry/nonebot-plugin-gocqhttp',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.3,<4.0.0',
}


setup(**setup_kwargs)
