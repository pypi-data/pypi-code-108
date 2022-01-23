# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['drf_kit', 'drf_kit.models', 'drf_kit.views']

package_data = \
{'': ['*']}

install_requires = \
['Django>=3,<5',
 'django-filter>=21.1,<22.0',
 'django-ordered-model>=3.5,<4.0',
 'djangorestframework>=3,<4',
 'drf-extensions>=0.7,<0.8']

setup_kwargs = {
    'name': 'drf-kit',
    'version': '1.11.0rc2',
    'description': 'DRF Toolkit',
    'long_description': None,
    'author': 'eduK',
    'author_email': 'pd@eduk.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
