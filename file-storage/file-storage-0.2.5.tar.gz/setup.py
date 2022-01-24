# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['file_storage']

package_data = \
{'': ['*']}

install_requires = \
['boto3>=1.17.66,<2.0.0']

setup_kwargs = {
    'name': 'file-storage',
    'version': '0.2.5',
    'description': 'Universal tool for file storages',
    'long_description': None,
    'author': 'Moleque',
    'author_email': 'molecada@yandex.ru',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
