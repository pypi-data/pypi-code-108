# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['echo1_coco_builder']

package_data = \
{'': ['*']}

install_requires = \
['marshmallow>=3.14.1,<4.0.0', 'pandas>=1.3.5,<2.0.0']

setup_kwargs = {
    'name': 'echo1-coco-builder',
    'version': '0.1.0',
    'description': '',
    'long_description': '',
    'author': 'Michael Mohamed',
    'author_email': 'michael.mohamed@echo1.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/e1-io/echo1-coco-builder',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.1,<4.0',
}


setup(**setup_kwargs)
