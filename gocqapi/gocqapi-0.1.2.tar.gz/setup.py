# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['gocqapi']

package_data = \
{'': ['*']}

install_requires = \
['httpx>=0.21.3,<0.22.0',
 'nonebot-adapter-cqhttp>=2.0.0-beta.1,<3.0.0',
 'nonebot2>=2.0.0-beta.1,<3.0.0',
 'pydantic>=1.9.0,<2.0.0']

setup_kwargs = {
    'name': 'gocqapi',
    'version': '0.1.2',
    'description': 'go-cqhttp API typing annoations, return data models and utils for nonebot',
    'long_description': None,
    'author': '风屿',
    'author_email': 'i@windis.cn',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.3,<3.10',
}


setup(**setup_kwargs)
