# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nonebot_plugin_roll']

package_data = \
{'': ['*']}

install_requires = \
['nonebot-adapter-onebot>=2.0.0-beta.1,<3.0.0', 'nonebot2>=2.0.0-beta.1,<3.0.0']

setup_kwargs = {
    'name': 'nonebot-plugin-roll',
    'version': '0.2.0',
    'description': 'Roll a dice!',
    'long_description': '<div align="center">\n\n# Roll\n\n<!-- prettier-ignore-start -->\n<!-- markdownlint-disable-next-line MD036 -->\n_🎲 扔骰子 🎲_\n<!-- prettier-ignore-end -->\n\n</div>\n\n<p align="center">\n  \n  <a href="https://github.com/KafCoppelia/nonebot_plugin_roll/blob/main/LICENSE">\n    <img src="https://img.shields.io/badge/license-MIT-informational">\n  </a>\n  \n  <a href="https://github.com/nonebot/nonebot2">\n    <img src="https://img.shields.io/badge/nonebot2-2.0.0beta.1-green">\n  </a>\n  \n  <a href="">\n    <img src="https://img.shields.io/badge/release-v0.2.0-orange">\n  </a>\n  \n</p>\n\n</p>\n\n## 版本\n\nv0.2.0\n\n⚠ 适配nonebot2-2.0.0beta.1；适配alpha.16版本参见[alpha.16分支](https://github.com/KafCoppelia/nonebot_plugin_roll/tree/alpha.16)\n\n## 安装\n\n1. 通过`pip`或`nb`安装，版本请指定`^0.2.0`；\n\n2. Enjoy:tada:\n\n## 功能\n\n掷骰！扔出指定个数的多面骰子。\n\n## 命令\n\nrd、roll、掷骰，后接“[x]d[y]”， x指定个数，y指骰子面数。\n\n## 本插件改自Omega-Miya roll点抽奖插件\n\n[Omega Miya](https://github.com/Ailitonia/omega-miya)',
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
