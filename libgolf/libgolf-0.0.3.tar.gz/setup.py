# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['libgolf']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'libgolf',
    'version': '0.0.3',
    'description': 'Common utilities for implementing golfing language builtin libraries',
    'long_description': '# libgolf\nCommon utilities for writing golfing language builtin libraries\n',
    'author': 'pxeger',
    'author_email': '_@pxeger.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/pxeger/libgolf',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
