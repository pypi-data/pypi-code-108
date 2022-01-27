# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['chalicelib', 'chalicelib.checks', 'chalicelib.checks.helpers']

package_data = \
{'': ['*']}

install_requires = \
['Jinja2==2.10.1',
 'MarkupSafe==1.1.1',
 'PyJWT==1.5.3',
 'cgap-pipeline-utils==23.0',
 'click>=7.1.2,<8.0.0',
 'dcicutils>=3.1.0,<4.0.0',
 'elasticsearch-dsl>=6.4.0,<7.0.0',
 'elasticsearch>=6.8.1,<7.0.0',
 'foursight-core>=0.5.0,<0.6.0',
 'geocoder==1.38.1',
 'gitpython>=3.1.2,<4.0.0',
 'google-api-python-client>=1.12.5,<2.0.0',
 'magma-suite>=0.2.8,<0.3.0',
 'pytest==5.1.2',
 'pytz>=2020.1,<2021.0',
 'tibanna-ff>=0.24.0,<0.25.0']

setup_kwargs = {
    'name': 'foursight-cgap',
    'version': '1.4.2',
    'description': 'Serverless Chalice Application for Monitoring',
    'long_description': None,
    'author': '4DN-DCIC Team',
    'author_email': 'support@4dnucleome.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.1,<3.7',
}


setup(**setup_kwargs)
