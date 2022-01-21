# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': '..'}

packages = \
['nonebot_plugin_datastore']

package_data = \
{'': ['*'], 'nonebot_plugin_datastore': ['dist/*']}

install_requires = \
['nonebot-plugin-localstore>=0.1.0,<0.2.0',
 'nonebot2>=2.0.0-beta.1,<3.0.0',
 'sqlmodel>=0.0.6,<0.0.7']

setup_kwargs = {
    'name': 'nonebot-plugin-datastore',
    'version': '0.0.1',
    'description': '适用于 Nonebot2 的数据存储插件',
    'long_description': None,
    'author': 'hemengyang',
    'author_email': 'hmy0119@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.3,<4.0.0',
}


setup(**setup_kwargs)
