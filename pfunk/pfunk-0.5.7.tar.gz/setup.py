# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pfunk',
 'pfunk.contrib',
 'pfunk.contrib.auth',
 'pfunk.contrib.ecommerce',
 'pfunk.contrib.email',
 'pfunk.tests',
 'pfunk.utils',
 'pfunk.web',
 'pfunk.web.views']

package_data = \
{'': ['*'], 'pfunk.tests': ['templates/auth/*', 'templates/email/*']}

install_requires = \
['Werkzeug>=2.0.1,<3.0.0',
 'bleach>=4.1.0,<5.0.0',
 'boto3>=1.18.36,<2.0.0',
 'cachetools>=4.2.2,<5.0.0',
 'click>=8.0.1,<9.0.0',
 'cryptography>=3.4.7,<4.0.0',
 'decorator>=5.0.9,<6.0.0',
 'envs>=1.3,<2.0',
 'faunadb>=4.0.1,<5.0.0',
 'graphql-py>=0.8.1,<0.9.0',
 'jinja2==3.0.1',
 'pip>=21.2.4,<22.0.0',
 'pyjwt>=2.1.0,<3.0.0',
 'pytz>=2021.1,<2022.0',
 'requests>=2.23.0,<3.0.0',
 'sammy>=0.4.3,<0.5.0',
 'stripe>=2.61.0,<3.0.0',
 'valley>=1.5.6,<2.0.0']

entry_points = \
{'console_scripts': ['pfunk = pfunk.cli:pfunk']}

setup_kwargs = {
    'name': 'pfunk',
    'version': '0.5.7',
    'description': 'A Python library created make building FaunaDB GraphQL schemas and authentication code easier.',
    'long_description': None,
    'author': 'Brian Jinwright',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
