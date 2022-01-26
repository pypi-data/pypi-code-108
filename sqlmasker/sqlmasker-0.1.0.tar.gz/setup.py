# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sqlmasker']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'sqlmasker',
    'version': '0.1.0',
    'description': 'n',
    'long_description': None,
    'author': 'Cazqew Powered',
    'author_email': 'nikprotect@protonmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
