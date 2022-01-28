# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['aejuice_base_logger']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'aejuice-base-logger',
    'version': '1.0.0',
    'description': 'Logger package for using with AEJuice python services',
    'long_description': None,
    'author': 'chloyka',
    'author_email': 'chloyka@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
