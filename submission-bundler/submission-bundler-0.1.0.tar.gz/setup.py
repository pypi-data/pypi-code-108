# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['bundle_submission']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'submission-bundler',
    'version': '0.1.0',
    'description': 'A package to bundle and generate submission file for competitive-programming. ',
    'long_description': None,
    'author': 'Hiroshi Tsuyuki',
    'author_email': 'kagemeka1@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.9,<3.10',
}


setup(**setup_kwargs)
