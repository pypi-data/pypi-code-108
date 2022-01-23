# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['django_cloud_tasks',
 'django_cloud_tasks.management',
 'django_cloud_tasks.management.commands']

package_data = \
{'': ['*']}

install_requires = \
['django>=3,<5', 'gcp-pilot[pubsub,tasks]']

setup_kwargs = {
    'name': 'django-google-cloud-tasks',
    'version': '0.10.0',
    'description': 'Async Tasks with HTTP endpoints',
    'long_description': None,
    'author': 'Joao Daher',
    'author_email': 'joao@daher.dev',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
