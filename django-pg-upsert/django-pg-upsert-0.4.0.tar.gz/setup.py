# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['django_pg_upsert']

package_data = \
{'': ['*']}

install_requires = \
['Django>=2.2']

setup_kwargs = {
    'name': 'django-pg-upsert',
    'version': '0.4.0',
    'description': 'Support Postgres native upsert (INSERT ... ON CONFLICT) for django',
    'long_description': None,
    'author': 'Semyon Pupkov',
    'author_email': 'mail@semyonpupkov.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<3.10',
}


setup(**setup_kwargs)
