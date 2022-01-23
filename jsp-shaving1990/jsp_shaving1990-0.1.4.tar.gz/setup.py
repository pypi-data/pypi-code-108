# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['jsp_shaving1990', 'jsp_shaving1990.utils']

package_data = \
{'': ['*']}

install_requires = \
['jps-algo>=0.1.3,<0.2.0', 'jsp-exp>=0.1.31,<0.2.0']

setup_kwargs = {
    'name': 'jsp-shaving1990',
    'version': '0.1.4',
    'description': 'J, Carlier.らの1990年の論文を実装したもの',
    'long_description': None,
    'author': '鈴木貴大',
    'author_email': 'merioda.seven.24@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/tkp0331/jsp-shaving1990',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.9,<4.0.0',
}


setup(**setup_kwargs)
