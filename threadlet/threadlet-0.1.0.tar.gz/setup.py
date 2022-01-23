# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['threadlet']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'threadlet',
    'version': '0.1.0',
    'description': 'Improved `Thread` and `ThreadPoolExecutor` classes.',
    'long_description': None,
    'author': 'Andrii Kuzmin',
    'author_email': 'jack.cvr@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
