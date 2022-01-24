# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nonebot_plugin_songpicker2']

package_data = \
{'': ['*']}

install_requires = \
['build>=0.1.0,<0.2.0',
 'httpx>=0.21.3,<0.22.0',
 'nonebot-adapter-onebot>=2.0.0-beta.1,<3.0.0',
 'nonebot2>=2.0.0-beta.1,<3.0.0',
 'twine>=3.3.0,<4.0.0']

setup_kwargs = {
    'name': 'nonebot-plugin-songpicker2',
    'version': '0.1.5',
    'description': '',
    'long_description': None,
    'author': 'Maximilian Wu',
    'author_email': 'me@maxng.cc',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
