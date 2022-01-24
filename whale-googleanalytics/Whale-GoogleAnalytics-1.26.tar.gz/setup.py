# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['whale_googleanalytics',
 'whale_googleanalytics.server',
 'whale_googleanalytics.server.helpers',
 'whale_googleanalytics.server.models',
 'whale_googleanalytics.server.routes']

package_data = \
{'': ['*']}

install_requires = \
['fastapi>=0.70.0,<0.71.0',
 'gino[pg,starlette]>=1.0.1,<2.0.0',
 'google-api-python-client>=2.31.0,<3.0.0',
 'gunicorn>=20.1.0,<21.0.0',
 'oauth2client>=4.1.3,<5.0.0',
 'pandas>=1.3.4,<2.0.0',
 'plotly>=5.4.0,<6.0.0',
 'psycopg2-binary>=2.9.2,<3.0.0',
 'uvicorn>=0.15.0,<0.16.0']

entry_points = \
{'console_scripts': ['start = whale_googleanalytics.main:start']}

setup_kwargs = {
    'name': 'whale-googleanalytics',
    'version': '1.26',
    'description': 'This library is used to fetch data from Google Analytics GA v4 and MCF v3',
    'long_description': None,
    'author': 'PO Boisvert',
    'author_email': 'you@example.com',
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
