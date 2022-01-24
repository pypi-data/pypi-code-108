# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['django_toolshed', 'django_toolshed.management.commands']

package_data = \
{'': ['*'],
 'django_toolshed': ['static/django_toolshed/css/*',
                     'static/django_toolshed/images/*',
                     'static/django_toolshed/js/*',
                     'templates/django_toolshed/*']}

install_requires = \
['Django>=4.0.1,<5.0.0',
 'celery>=5.2.1,<6.0.0',
 'django-click>=2.2.0,<3.0.0',
 'djangorestframework>=3.13.1,<4.0.0',
 'ipython_genutils>=0.2.0,<0.3.0',
 'iterfzf>=0.5.0,<0.6.0']

entry_points = \
{'console_scripts': ['celery-auto-app = '
                     'django_toolshed.celery_auto_app:command']}

setup_kwargs = {
    'name': 'django-toolshed',
    'version': '0.5.2',
    'description': '',
    'long_description': None,
    'author': 'Dani Hodovic',
    'author_email': 'you@example.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
