# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['notification', 'notification.migrations']

package_data = \
{'': ['*']}

install_requires = \
['channels>=3.0.4',
 'django-filter>=21.1',
 'django>=3.2',
 'djangorestframework>=3.13.1',
 'uvicorn>=0.16.0']

setup_kwargs = {
    'name': 'django-user-notification',
    'version': '0.4.1',
    'description': 'Django message notification package',
    'long_description': '# django-user-notification\n',
    'author': 'Aiden Lu',
    'author_email': 'allaher@icloud.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/aiden520/django-user-notification',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8',
}


setup(**setup_kwargs)
