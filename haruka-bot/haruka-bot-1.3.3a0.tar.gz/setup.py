# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src\\plugins'}

packages = \
['haruka_bot',
 'haruka_bot.cli',
 'haruka_bot.database',
 'haruka_bot.libs',
 'haruka_bot.plugins',
 'haruka_bot.plugins.at',
 'haruka_bot.plugins.dynamic',
 'haruka_bot.plugins.live',
 'haruka_bot.plugins.permission',
 'haruka_bot.plugins.pusher',
 'haruka_bot.plugins.sub',
 'haruka_bot.utils']

package_data = \
{'': ['*']}

install_requires = \
['appdirs>=1.4.4,<2.0.0',
 'click>=8.0.1,<9.0.0',
 'httpx>=0.18.2,<0.19.0',
 'nonebot-adapter-onebot>=2.0.0-beta.1,<3.0.0',
 'nonebot-plugin-apscheduler>=0.1.2,<0.2.0',
 'nonebot2>=2.0.0-beta.1,<3.0.0',
 'packaging>=20.9,<21.0',
 'pillow>=8.2.0,<9.0.0',
 'playwright>=1.15.0,<2.0.0',
 'pydantic>=1.8.2,<2.0.0',
 'python-dotenv>=0.17.1,<0.18.0',
 'rsa>=4.7.2,<5.0.0',
 'tortoise-orm[asyncpg]>=0.17.3,<0.18.0']

entry_points = \
{'console_scripts': ['hb = haruka_bot.cli.__main__:main']}

setup_kwargs = {
    'name': 'haruka-bot',
    'version': '1.3.3a0',
    'description': 'Push dynamics and live informations from bilibili to QQ. Based on nonebot2.',
    'long_description': '[![HarukaBot](https://socialify.git.ci/SK-415/HarukaBot/image?description=1&font=Source%20Code%20Pro&forks=1&issues=1&language=1&logo=https%3A%2F%2Fraw.githubusercontent.com%2FSK-415%2FHarukaBot%2Fmaster%2Fdocs%2F.vuepress%2Fpublic%2Flogo.png&owner=1&pattern=Charlie%20Brown&stargazers=1&theme=Dark)](https://haruka-bot.sk415.icu/)\n\n# [HarukaBot](https://haruka-bot.sk415.icu)——优雅的 B 站推送 QQ 机器人\n\n名称来源：[@白神遥Haruka](https://space.bilibili.com/477332594)\n\nLogo 画师：[@Ratto](https://space.bilibili.com/23242907)\n\n[![VERSION](https://img.shields.io/pypi/v/haruka-bot)](https://haruka-bot.sk415.icu/about/CHANGELOG.html)\n[![qq group](https://img.shields.io/badge/QQ%E7%BE%A4-629574472-orange)](https://jq.qq.com/?_wv=1027&k=sHPbCRAd)\n[![time tracker](https://wakatime.com/badge/github/SK-415/HarukaBot.svg)](https://wakatime.com/badge/github/SK-415/HarukaBot)\n\n## 简介\n\n一款将哔哩哔哩 UP 主的直播与动态信息推送至 QQ 的机器人。基于 [NoneBot2](https://github.com/nonebot/nonebot2) 开发，前身为 [dd-bot](https://github.com/SK-415/dd-bot) 。\n\n## 特色功能\n\nHarukaBot 针对不同的推送场景（粉丝群、娱乐群、直播通知群），提供了个性化设置：\n\n- 自定义推送内容，每位 UP 主可限制仅动态、仅直播。\n- 群内开启权限限制，仅管理员以上可以使用机器人。\n- 指定推送内容@全体成员，次数用光自动忽略。\n- 同时连接多个 QQ 号，避免@全体成员次数不够。\n\n## [文档（点击查看）](https://haruka-bot.sk415.icu)\n\n## 特别感谢\n\n- [@mnixry](https://github.com/mnixry)：感谢混淆佬为本项目提供的**技♂术指导**。\n- [@wosiwq](https://github.com/wosiwq)：感谢 W 桑撰写的「小小白白话文」。\n- [NoneBot2](https://github.com/nonebot/nonebot2)：HarukaBot 使用的开发框架。\n- [go-cqhttp](https://github.com/Mrs4s/go-cqhttp)：稳定完善的 CQHTTP 实现。\n- [bilibili-API-collect](https://github.com/SocialSisterYi/bilibili-API-collect)：非常详细的 B 站 API 文档。\n- [bilibili_api](https://github.com/Passkou/bilibili_api)：Python 实现的 B 站 API 库。\n\n## 支持与贡献\n\n觉得好用可以给这个项目点个 Star 或者去 [爱发电](https://afdian.net/@HarukaBot) 投喂我。\n\n有意见或者建议也欢迎提交 [Issues](https://github.com/SK-415/HarukaBot/issues) 和 [Pull requests](https://github.com/SK-415/HarukaBot/pulls)。\n\n## 许可证\n本项目使用 [GNU AGPLv3](https://choosealicense.com/licenses/agpl-3.0/) 作为开源许可证。\n',
    'author': 'SK-415',
    'author_email': '2967923486@qq.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/SK-415/HarukaBot',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
