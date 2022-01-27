# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tmp_folder']

package_data = \
{'': ['*']}

install_requires = \
['typing-extensions>=4.0.1,<5.0.0']

setup_kwargs = {
    'name': 'tmp-folder',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Jorge Alvarado',
    'author_email': 'alvaradosegurajorge@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
