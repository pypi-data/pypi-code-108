# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['admin_data_views', 'admin_data_views.templatetags']

package_data = \
{'': ['*'], 'admin_data_views': ['templates/admin_data_views/*']}

install_requires = \
['Django>=3.2', 'django-settings-holder>=0.0.2']

setup_kwargs = {
    'name': 'django-admin-data-views',
    'version': '0.1.0',
    'description': 'Add custom data views to django admin panel.',
    'long_description': '# Django Admin Data Views\n\n[![Coverage Status](https://coveralls.io/repos/github/MrThearMan/django-admin-data-views/badge.svg?branch=main)](https://coveralls.io/github/MrThearMan/django-admin-data-views?branch=main)\n[![GitHub Workflow Status](https://img.shields.io/github/workflow/status/MrThearMan/django-admin-data-views/Tests)](https://github.com/MrThearMan/django-admin-data-views/actions/workflows/main.yml)\n[![PyPI](https://img.shields.io/pypi/v/django-admin-data-views)](https://pypi.org/project/django-admin-data-views)\n[![GitHub](https://img.shields.io/github/license/MrThearMan/django-admin-data-views)](https://github.com/MrThearMan/django-admin-data-views/blob/main/LICENSE)\n[![GitHub last commit](https://img.shields.io/github/last-commit/MrThearMan/django-admin-data-views)](https://github.com/MrThearMan/django-admin-data-views/commits/main)\n[![GitHub issues](https://img.shields.io/github/issues-raw/MrThearMan/django-admin-data-views)](https://github.com/MrThearMan/django-admin-data-views/issues)\n\n\n[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/django-admin-data-views)](https://pypi.org/project/django-admin-data-views)\n[![PyPI - Django Version](https://img.shields.io/pypi/djversions/django-admin-data-views)](https://pypi.org/project/django-admin-data-views)\n\n```shell\npip install django-admin-data-views\n```\n\n---\n\n**Documentation**: [https://mrthearman.github.io/django-admin-data-views/](https://mrthearman.github.io/django-admin-data-views/)\n\n**Source Code**: [https://github.com/MrThearMan/django-admin-data-views](https://github.com/MrThearMan/django-admin-data-views)\n\n---\n\nDjango Admin Data Views enables you to easily add non-model data to the django admin panel.\nData from an API or file can be shown in similar table and item views than regular models.\n',
    'author': 'Matti Lamppu',
    'author_email': 'lamppu.matti.akseli@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/MrThearMan/django-admin-data-views',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4',
}


setup(**setup_kwargs)
