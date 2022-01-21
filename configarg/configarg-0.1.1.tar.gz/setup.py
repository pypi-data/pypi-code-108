# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['configarg']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'configarg',
    'version': '0.1.1',
    'description': 'Configuration file with argparse',
    'long_description': None,
    'author': 'NEWROPE Co. Ltd.',
    'author_email': 'dev@newrope.biz',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
