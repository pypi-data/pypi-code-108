# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nonebot_plugin_chess']

package_data = \
{'': ['*']}

install_requires = \
['nonebot-adapter-onebot>=2.0.0-beta.1,<3.0.0',
 'nonebot-plugin-htmlrender>=0.0.4,<0.0.5',
 'nonebot2>=2.0.0-beta.1,<3.0.0']

setup_kwargs = {
    'name': 'nonebot-plugin-chess',
    'version': '0.1.0',
    'description': '适用于 Nonebot2 的棋类游戏插件',
    'long_description': '# nonebot-plugin-chess\n\n适用于 [Nonebot2](https://github.com/nonebot/nonebot2) 的棋类游戏插件。\n\n抄自隔壁 koishi（：[koishi-plugin-chess](https://github.com/koishijs/koishi-plugin-chess)\n',
    'author': 'meetwq',
    'author_email': 'meetwq@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/MeetWq/nonebot-plugin-chess',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.3,<4.0.0',
}


setup(**setup_kwargs)
