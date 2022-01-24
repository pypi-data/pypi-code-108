# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nonebot_plugin_atri']

package_data = \
{'': ['*'], 'nonebot_plugin_atri': ['resources/text/*', 'resources/voice/*']}

install_requires = \
['nonebot-adapter-onebot>=2.0.0-beta.1,<3.0.0', 'nonebot2>=2.0.0-beta.1,<3.0.0']

setup_kwargs = {
    'name': 'nonebot-plugin-atri',
    'version': '0.0.3',
    'description': '高い性能萝卜子',
    'long_description': None,
    'author': '风屿',
    'author_email': 'i@windis.cn',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
