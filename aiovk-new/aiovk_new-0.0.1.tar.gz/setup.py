# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['aiovk_new',
 'aiovk_new.audio',
 'aiovk_new.models',
 'aiovk_new.models.attachments',
 'aiovk_new.wall']

package_data = \
{'': ['*']}

install_requires = \
['httpx>=0.21.3,<0.22.0', 'pydantic>=1.9.0,<2.0.0']

setup_kwargs = {
    'name': 'aiovk-new',
    'version': '0.0.1',
    'description': 'A simple async library for vk with pydantic & httpx',
    'long_description': None,
    'author': 'Daniel Zakharov',
    'author_email': 'daniel734@bk.ru',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
