# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['flypper_redis', 'flypper_redis.storage']

package_data = \
{'': ['*']}

modules = \
['README', 'LICENSE']
install_requires = \
['flypper>=0.1.0,<0.2.0', 'redis>=3.5.3,<4.0.0']

setup_kwargs = {
    'name': 'flypper-redis',
    'version': '0.1.1',
    'description': '',
    'long_description': None,
    'author': 'Nicolas Zermati',
    'author_email': 'nicoolas25@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'py_modules': modules,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
