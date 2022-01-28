# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['omni_cv_rules', 'omni_cv_rules.coconut']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'omni-cv-rules',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Kento Masui',
    'author_email': 'nameissoap@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
