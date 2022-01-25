# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['celery_typed_tasks']

package_data = \
{'': ['*']}

install_requires = \
['celery>=5.0.0,<6.0.0']

setup_kwargs = {
    'name': 'celery-typed-tasks',
    'version': '0.1.21',
    'description': '',
    'long_description': None,
    'author': 'massover',
    'author_email': 'joshm@simplebet.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4',
}


setup(**setup_kwargs)
