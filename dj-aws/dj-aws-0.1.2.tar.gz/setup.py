# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['djaws',
 'djaws.cognito',
 'djaws.management',
 'djaws.management.commands',
 'djaws.s3',
 'djaws.tests',
 'djaws.tests.schemas',
 'djaws.tests.schemas.cognito',
 'djaws.tests.schemas.s3']

package_data = \
{'': ['*']}

install_requires = \
['Django>=3.2.4,<3.3.0',
 'PyJWT[crypto]>=2.3.0,<3.0.0',
 'boto3>=1.20.35,<1.21.0',
 'dj-starter>=0.1.1,<0.2.0',
 'django-environ>=0.8.1,<0.9.0',
 'psycopg2-binary>=2.9.2,<3.0.0']

setup_kwargs = {
    'name': 'dj-aws',
    'version': '0.1.2',
    'description': 'Django + AWS made easy',
    'long_description': None,
    'author': 'Adrian',
    'author_email': 'adrian@rydeas.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/adrianmeraz/dj-aws',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
