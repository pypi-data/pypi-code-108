# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['metaphor',
 'metaphor.bigquery',
 'metaphor.bigquery.profile',
 'metaphor.bigquery.usage',
 'metaphor.common',
 'metaphor.dbt',
 'metaphor.dbt.generated',
 'metaphor.google_directory',
 'metaphor.looker',
 'metaphor.metabase',
 'metaphor.postgresql',
 'metaphor.redshift',
 'metaphor.redshift.usage',
 'metaphor.slack_directory',
 'metaphor.snowflake',
 'metaphor.snowflake.profile',
 'metaphor.snowflake.usage',
 'metaphor.tableau']

package_data = \
{'': ['*'], 'metaphor.common': ['docs/*']}

install_requires = \
['aws-assume-role-lib>=1.3.0,<2.0.0',
 'boto3>=1.17.53,<1.18.0',
 'botocore>=1.20.53,<1.21.0',
 'canonicaljson>=1.4.0,<2.0.0',
 'fastjsonschema>=2.15.1,<2.16.0',
 'metaphor-models>=0.6.15,<0.7.0',
 'pyserde[yaml]>=0.4.0,<0.5.0',
 'python-dateutil>=2.8.1,<2.9.0',
 'requests>=2.25.1,<3.0.0',
 'smart-open>=5.0.0,<6.0.0']

extras_require = \
{'all': ['asyncpg>=0.22.0,<0.23.0',
         'google-api-python-client>=2.29.0,<2.30.0',
         'google-auth-oauthlib>=0.4.4,<0.5.0',
         'google-cloud-bigquery>=2.21.0,<3.0.0',
         'google-cloud-logging>=2.7.0,<3.0.0',
         'lkml>=1.1.0,<2.0.0',
         'looker-sdk>=21.4.1,<22.0.0',
         'slack-sdk>=3.5.1,<4.0.0',
         'snowflake-connector-python>=2.7.0,<2.8.0',
         'sql-metadata==2.2.2',
         'tableauserverclient>=0.17.0,<0.18.0'],
 'bigquery': ['google-cloud-bigquery>=2.21.0,<3.0.0',
              'google-cloud-logging>=2.7.0,<3.0.0'],
 'dbt': ['pydantic>=1.8.2,<2.0.0'],
 'google_directory': ['google-api-python-client>=2.29.0,<2.30.0',
                      'google-auth-oauthlib>=0.4.4,<0.5.0'],
 'looker': ['lkml>=1.1.0,<2.0.0',
            'looker-sdk>=21.4.1,<22.0.0',
            'sql-metadata==2.2.2'],
 'postgresql': ['asyncpg>=0.22.0,<0.23.0'],
 'redshift': ['asyncpg>=0.22.0,<0.23.0'],
 'slack_directory': ['slack-sdk>=3.5.1,<4.0.0'],
 'snowflake': ['snowflake-connector-python>=2.7.0,<2.8.0',
               'sql-metadata==2.2.2'],
 'tableau': ['tableauserverclient>=0.17.0,<0.18.0']}

setup_kwargs = {
    'name': 'metaphor-connectors',
    'version': '0.10.2',
    'description': '',
    'long_description': None,
    'author': 'Metaphor',
    'author_email': 'dev@metaphor.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<3.11',
}


setup(**setup_kwargs)
