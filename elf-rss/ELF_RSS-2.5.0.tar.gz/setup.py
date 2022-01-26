# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src/plugins'}

packages = \
['ELF_RSS2',
 'ELF_RSS2.RSS',
 'ELF_RSS2.RSS.routes',
 'ELF_RSS2.RSS.routes.Parsing']

package_data = \
{'': ['*']}

install_requires = \
['ImageHash>=4.2.0,<5.0.0',
 'Pillow>=9.0.0,<10.0.0',
 'arrow>=1.2.0,<2.0.0',
 'bbcode>=1.1.0,<2.0.0',
 'emoji>=0.5.4,<0.6.0',
 'feedparser>=6.0.0,<7.0.0',
 'google-trans-new>=1.1.9,<2.0.0',
 'httpx>=0.18.0,<0.19.0',
 'magneturi>=1.3,<2.0',
 'nonebot-adapter-onebot==2.0.0b1',
 'nonebot-plugin-apscheduler>=0.1.2,<0.2.0',
 'nonebot2==2.0.0b1',
 'pydantic>=1.9.0,<2.0.0',
 'pyquery>=1.4.3,<2.0.0',
 'python-qbittorrent>=0.4.2,<0.5.0',
 'tenacity>=7.0.0,<8.0.0',
 'tinydb>=4.6.1,<5.0.0',
 'typing-extensions>=3.10.0.2,<4.0.0.0']

setup_kwargs = {
    'name': 'elf-rss',
    'version': '2.5.0',
    'description': 'ELF_RSS',
    'long_description': '# ELF_RSS\n\n[![Codacy Badge](https://app.codacy.com/project/badge/Grade/b799d894ed354d5999fb6047543c494c)](https://www.codacy.com/gh/Quan666/ELF_RSS/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=Quan666/ELF_RSS&amp;utm_campaign=Badge_Grade)\n[![QQ Group](https://img.shields.io/badge/qq%E7%BE%A4-984827132-orange?style=flat-square)](https://jq.qq.com/?_wv=1027&k=sST08Nkd)\n\n> 1. 容易使用的命令\n> 2. 更规范的代码，方便移植到你自己的机器人\n> 3. 使用全新的 [Nonebot2](https://v2.nonebot.dev/guide/) 框架\n\n这是一个以 Python 编写的 QQ 机器人插件，用于订阅 RSS 并实时以 QQ消息推送。\n\n算是第一次用 Python 写出来的比较完整、实用的项目。代码比较难看，正在重构中\n\n---\n\n当然也有很多插件能够做到订阅 RSS ，但不同的是，大多数都需要在服务器上修改相应配置才能添加订阅，而该插件只需要发送QQ消息给机器人就能动态添加订阅。\n\n对于订阅，支持QQ、QQ群的单个、多个订阅\n\n每个订阅的个性化设置丰富，能够应付多种场景。\n\n## 功能介绍\n\n* 发送QQ消息来动态增、删、查、改 RSS 订阅\n* 订阅内容翻译（使用谷歌机翻，可设置为百度翻译）\n* 个性化订阅设置（更新频率、翻译、仅标题、仅图片等）\n* 多平台支持\n* 图片压缩后发送\n* 种子下载并上传到群文件\n* 消息支持根据链接、标题、图片去重\n* 可设置只发送限定数量的图片，防止刷屏\n* 可设置从正文中要移除的指定内容，支持正则\n\n## 文档目录\n\n> 注意：推荐 Python 3.8.3+ 版本 Windows版安装包下载地址：[https://www.python.org/ftp/python/3.8.3/python-3.8.3-amd64.exe](https://www.python.org/ftp/python/3.8.3/python-3.8.3-amd64.exe)\n>\n> * [部署教程](docs/部署教程.md)\n> * [使用教程](docs/2.0%20使用教程.md)\n> * [使用教程 旧版](docs/1.0%20使用教程.md)\n> * [常见问题](docs/常见问题.md)\n> * [更新日志](docs/更新日志.md)\n\n## 效果预览\n\n![image-20201221163514747](https://cdn.jsdelivr.net/gh/Quan666/CDN/pic/image-20201221163514747.png)\n\n![image-20201221163555086](https://cdn.jsdelivr.net/gh/Quan666/CDN/pic/image-20201221163555086.png)\n\n![image-20201221163721358](https://cdn.jsdelivr.net/gh/Quan666/CDN/pic/image-20201221163721358.png)\n\n![image](https://user-images.githubusercontent.com/32663291/117431780-3373a100-af5c-11eb-9de2-ff75948abf1c.png)\n\n## TODO\n\n* [x] 1. 订阅信息保护，不在群组中输出订阅QQ、群组\n* [x] 2. 更为强大的检查更新时间设置\n* [x] 3. RSS 源中 torrent 自动下载并上传至订阅群（适合番剧订阅）\n* [ ] 4. 暂停检查订阅更新\n* [ ] 5. 模糊匹配订阅名\n* [ ] 6. 性能优化，全部替换为异步操作\n\n## 感谢以下项目或服务\n\n不分先后\n\n* [RSSHub](https://github.com/DIYgod/RSSHub)\n* [Nonebot](https://github.com/nonebot/nonebot2)\n* [酷Q（R. I. P）](https://cqp.cc/)\n* [coolq-http-api](https://github.com/richardchien/coolq-http-api)\n* [go-cqhttp](https://github.com/Mrs4s/go-cqhttp)\n',
    'author': 'Quan666',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Quan666/ELF_RSS',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8.3,<4.0.0',
}


setup(**setup_kwargs)
