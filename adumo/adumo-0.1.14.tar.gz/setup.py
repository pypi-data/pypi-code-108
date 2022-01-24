# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['adumo']

package_data = \
{'': ['*']}

install_requires = \
['environs>=9.4.0,<10.0.0', 'flake8>=4.0.1,<5.0.0', 'httpx>=0.21.3,<0.22.0']

setup_kwargs = {
    'name': 'adumo',
    'version': '0.1.14',
    'description': '',
    'long_description': None,
    'author': 'Wayne',
    'author_email': 'wayne@flickswitch.co.za',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
