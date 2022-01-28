# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nonebot_plugin_heweather']

package_data = \
{'': ['*'],
 'nonebot_plugin_heweather': ['templates/*',
                              'templates/css/*',
                              'templates/css/fonts/*']}

install_requires = \
['httpx>=0.18.0,<1.0.0',
 'nonebot-adapter-onebot==2.0.0-beta.1',
 'nonebot-plugin-htmlrender>=0.0.4.1']

setup_kwargs = {
    'name': 'nonebot-plugin-heweather',
    'version': '0.5.1',
    'description': 'Get Heweather information and convert to pictures',
    'long_description': '# nonebot-plugin-heweather\n\n获取和风天气信息并转换为图片\n\n# 使用html+playwright来渲染好看的！\n\n- 使用了~~自产自销的~~[nonebot-plugin-htmlrender](https://github.com/kexue-z/nonebot-plugin-htmlrender)\n- 需要先保证playwright可以正常运行并在系统（或容器中）存在中文字体\n\n\n# 安装\n\n直接使用 `pip install nonebot-plugin-heweather` 进行安装\n如果是`beta1` 需要 `pip install nonebot-plugin-heweather==0.4.1.1-beta.1`\n\n在 `bot.py` 中 写入 `nonebot.load_plugin("nonebot_plugin_heweather")`\n\n# 指令\n\n`天气+地区` 或 `地区+天气`\n\n# 配置\n\n## apikey 必须配置 环境配置\n\n```\nQWEATHER_APIKEY = xxx\n```\n\n## api类型 可选配置 环境配置\n\n0 = 普通版(3天天气预报)\n1 = 个人开发版(7天天气预报)\n2 = 商业版 (7天天气预报)\n\n\n```\nQWEATHER_APITYPE = \n```\n\n',
    'author': 'kexue',
    'author_email': 'x@kexue.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.3,<4.0.0',
}


setup(**setup_kwargs)
