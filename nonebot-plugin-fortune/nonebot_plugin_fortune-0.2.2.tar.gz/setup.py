# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nonebot_plugin_fortune']

package_data = \
{'': ['*'],
 'nonebot_plugin_fortune': ['resource/*',
                            'resource/font/*',
                            'resource/fortune/*',
                            'resource/img/genshin/*',
                            'resource/img/pcr/*',
                            'resource/img/touhou/*',
                            'resource/img/vtuber/*']}

install_requires = \
['nonebot-adapter-onebot>=2.0.0-beta.1,<3.0.0',
 'nonebot2>=2.0.0-beta.1,<3.0.0',
 'pillow>=9.0.0,<10.0.0',
 'ujson>=5.1.0,<6.0.0']

setup_kwargs = {
    'name': 'nonebot-plugin-fortune',
    'version': '0.2.2',
    'description': 'Fortune divination!',
    'long_description': '<div align="center">\n\n# Fortune\n\n<!-- prettier-ignore-start -->\n<!-- markdownlint-disable-next-line MD036 -->\n_🙏 今日运势 🙏_\n<!-- prettier-ignore-end -->\n\n</div>\n<p align="center">\n  \n  <a href="https://github.com/KafCoppelia/nonebot_plugin_fortune/blob/main/LICENSEE">\n    <img src="https://img.shields.io/badge/license-MIT-informational">\n  </a>\n  \n  <a href="https://github.com/nonebot/nonebot2">\n    <img src="https://img.shields.io/badge/nonebot2-2.0.0beta.1-green">\n  </a>\n  \n  <a href="">\n    <img src="https://img.shields.io/badge/release-v0.2.2-orange">\n  </a>\n  \n</p>\n\n</p>\n\n## 版本\n\nv0.2.2\n\n⚠ 适配nonebot2-2.0.0beta.1；适配alpha.16版本参见[alpha.16分支](https://github.com/KafCoppelia/nonebot_plugin_fortune/tree/alpha.16)\n\n## 安装\n\n1. 通过`pip`或`nb`安装，版本请指定`^0.2.2`；\n\n2. 抽签签底`img`、字体`font`、文案`fortune`等资源位于`./resource`下，可在`env`下设置`FORTUNE_PATH`更改；\n\n```python\nFORTUNE_PATH="your_path_to_resource"   # 默认位于os.path.join(os.path.dirname(__file__), "resource")，具体查看data_source.py\n```\n\n3. 占卜一下你的今日运势！🎉\n\n## 功能\n\n1. 随机抽取今日运势，配置四种抽签主题：原神、PCR、Vtuber、东方；\n\n2. 可设置随机抽签主题或指定主题，也可指定角色签底（例如可莉、魔理沙、凯露、**阿夸**🥰）；\n\n3. 每群每人一天限抽签1次，0点刷新（贪心的人是不会有好运的🤗）；\n\n4. 抽签的信息会保存在`./resource/fortune_data.json`内；群抽签设置保存在`./resource/fortune_setting.json`内；抽签生成的图片当天会保存在`./resource/out`下；\n\n## 命令\n\n1. 一般抽签：今日运势、抽签、运势；\n\n2. 指定签底并抽签：指定[xxx]签，具体配置位于`utils.py`下`SpecificTypeList`；\n\n3. [群管或群主或超管] 配置抽签主题：\n    - 设置[原神/pcr/东方/vtb]签：设置群抽签主题；\n\n    - 重置抽签：设置群抽签主题为随机；\n\n4. 抽签设置：查看当前群抽签主题的配置；\n\n## 效果\n\n测试效果出自群聊。\n\n![display](./display.jpg)\n\n## 本插件改自\n\n1. [opqqq-plugin](https://github.com/opq-osc/opqqq-plugin)，除功能函数外，由于要适配nonebot2，底层已大改；\n\n2. 感谢江樂丝提供东方签底~~实际上可能是东方老哥提供的~~；',
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
