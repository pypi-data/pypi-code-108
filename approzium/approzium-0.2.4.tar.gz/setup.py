# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['approzium',
 'approzium._mysql',
 'approzium._postgres',
 'approzium.asyncpg',
 'approzium.mysql',
 'approzium.mysql.connector',
 'approzium.opentelemetry',
 'approzium.psycopg2',
 'approzium.pymysql']

package_data = \
{'': ['*'], 'approzium': ['_protos/*']}

install_requires = \
['boto3>=1.14.10,<2.0.0',
 'ec2-metadata>=2.2.0,<3.0.0',
 'grpcio-tools>=1.30.0,<2.0.0',
 'grpcio>=1.30.0,<2.0.0']

extras_require = \
{'sqllibs': ['asyncpg>=0.20.1,<0.22.0',
             'mysql-connector-python>=8.0.20,<9.0.0',
             'psycopg2>=2.8.5,<3.0.0',
             'pymysql>=0.9.3,<0.10.0'],
 'tracing': ['opentelemetry-instrumentation-psycopg2>=0.23b2,<0.24',
             'opentelemetry-exporter-jaeger>=1.4.1,<2.0.0']}

setup_kwargs = {
    'name': 'approzium',
    'version': '0.2.4',
    'description': 'Approzium SDK provides Approzium database authentiation for Python',
    'long_description': None,
    'author': 'Cyral',
    'author_email': 'security@cyral.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/cyralinc/approzium',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
