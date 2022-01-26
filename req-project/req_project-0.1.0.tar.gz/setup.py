# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['req_project']

package_data = \
{'': ['*']}

install_requires = \
['strictdoc>=0.0.18,<0.0.19']

setup_kwargs = {
    'name': 'req-project',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Michael Naderhirn',
    'author_email': 'm.naderhirn@nmrobotic.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
