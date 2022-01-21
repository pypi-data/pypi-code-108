# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['metrics_layer',
 'metrics_layer.api',
 'metrics_layer.api.blueprints',
 'metrics_layer.api.models',
 'metrics_layer.cli',
 'metrics_layer.core',
 'metrics_layer.core.convert',
 'metrics_layer.core.model',
 'metrics_layer.core.parse',
 'metrics_layer.core.query',
 'metrics_layer.core.sql']

package_data = \
{'': ['*'], 'metrics_layer': ['webapp/*']}

install_requires = \
['GitPython>=3.1.20,<4.0.0',
 'PyPika>=0.48.8,<0.49.0',
 'PyYAML>=5.4.1,<6.0.0',
 'click>=8.0,<9.0',
 'colorama>=0.4.4,<0.5.0',
 'importlib-metadata>=4.8.2,<5.0.0',
 'lkml>=1.1.0,<2.0.0',
 'networkx>=2.6.3,<3.0.0',
 'requests>=2.26.0,<3.0.0',
 'sqlparse>=0.4.1,<0.5.0']

extras_require = \
{'all': ['pandas>=1.2.2,<2.0.0',
         'snowflake-connector-python>=2.5.1,<2.6.0',
         'pyarrow==3.0.0',
         'google-cloud-bigquery>=2.24.1,<3.0.0',
         'Flask',
         'Flask-RESTful>=0.3.9,<0.4.0',
         'Flask-SQLAlchemy>=2.5.1,<3.0.0',
         'Flask-Migrate>=3.1.0,<4.0.0',
         'gunicorn>=20.1.0,<21.0.0',
         'Flask-Bcrypt>=0.7.1,<0.8.0',
         'PyJWT>=2.1.0,<3.0.0',
         'dbt-core>=1.0.0,<2.0.0',
         'dbt-extractor>=0.4.0,<0.5.0',
         'dbt-snowflake>=1.0.0,<2.0.0',
         'dbt-bigquery>=1.0.0,<2.0.0'],
 'bigquery': ['pandas>=1.2.2,<2.0.0',
              'pyarrow==3.0.0',
              'google-cloud-bigquery>=2.24.1,<3.0.0',
              'dbt-bigquery>=1.0.0,<2.0.0'],
 'dbt': ['dbt-core>=1.0.0,<2.0.0', 'dbt-extractor>=0.4.0,<0.5.0'],
 'flask': ['Flask',
           'Flask-RESTful>=0.3.9,<0.4.0',
           'Flask-SQLAlchemy>=2.5.1,<3.0.0',
           'Flask-Migrate>=3.1.0,<4.0.0',
           'gunicorn>=20.1.0,<21.0.0',
           'Flask-Bcrypt>=0.7.1,<0.8.0',
           'PyJWT>=2.1.0,<3.0.0'],
 'snowflake': ['pandas>=1.2.2,<2.0.0',
               'snowflake-connector-python>=2.5.1,<2.6.0',
               'pyarrow==3.0.0',
               'dbt-snowflake>=1.0.0,<2.0.0']}

entry_points = \
{'console_scripts': ['metrics_layer = metrics_layer:cli_group',
                     'ml = metrics_layer:cli_group']}

setup_kwargs = {
    'name': 'metrics-layer',
    'version': '0.1.31',
    'description': 'The open source metrics layer.',
    'long_description': '# Metrics Layer\n\n[![Build Status](https://app.travis-ci.com/Zenlytic/metrics_layer.svg?branch=master)](https://app.travis-ci.com/Zenlytic/metrics_layer)\n[![codecov](https://codecov.io/gh/Zenlytic/metrics_layer/branch/master/graph/badge.svg?token=7JA6PKNV57)](https://codecov.io/gh/Zenlytic/metrics_layer)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n\n# What is Metrics Layer?\n\nMetrics Layer is an open source project with the goal of making access to metrics consistent throughout an organization. We believe you should be able to access consistent metrics from any tool you use to access data.\n\n## How does it work?\n\nRight now, the only supported BI tool is Looker. Metrics Layer will read your LookML and give you the ability to access those metrics and dimensions in a python client library, or through SQL with a special `MQL` tag.\n\nSound interesting? Here\'s how to set Metrics Layer up with Looker and start querying your metrics in **in under 2 minutes**.\n\n## Installation\n\nMake sure that your data warehouse is one of the supported types. Metrics Layer currently supports Snowflake and BigQuery, and only works with `python >= 3.7`.\n\nInstall Metrics Layer with the appropriate extra for your warehouse\n\nFor Snowflake run `pip install metrics-layer[snowflake]`\n\nFor BigQuery run `pip install metrics-layer[bigquery]`\n\n\n## Profile set up\n\nThere are several ways to set up a profile, we\'re going to look at the fastest one here, but look at [the docs](https://zenlytic.github.io/metrics_layer/docs/connection_setup/connecting) if you want more robust connection methods.\n\nThe fastest way to get connected is to pass the necessary information directly into Metrics Layer. Once you\'ve installed the library with the warehouse you need, you should be able to run the code snippet below and start querying.\n\nYou\'ll need to pull the repo with your LookML locally for this example or look at [the docs](https://zenlytic.github.io/metrics_layer/docs/connection_setup/connecting) for connections through GitHub directly or the Looker API.\n\n\n```\nfrom metrics_layer import MetricsLayerConnection\n\n# Give metrics_layer the info to connect to your data model and warehouse\nconfig = {\n  "repo_path": "~/Desktop/my-looker-repo",\n  "connections": [\n    {\n      "name": "mycompany",              # The name of the connection in LookML (you\'ll see this in model files)\n      "type": "snowflake",\n      "account": "2e12ewdq.us-east-1",\n      "username": "demo_user",\n      "password": "q23e13erfwefqw",\n      "database": "ANALYTICS",\n      "schema": "DEV",                  # Optional\n    }\n  ],\n}\nconn = MetricsLayerConnection(config)\n\n# You\'re off to the races. Query away!\ndf = conn.query(metrics=["total_revenue"], dimensions=["channel", "region"])\n```\n\nThat\'s it.\n\nFor more advanced methods of connection and more information about the project check out [the docs](https://zenlytic.github.io/metrics_layer/).\n',
    'author': 'Paul Blankley',
    'author_email': 'paul@zenlytic.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Zenlytic/metrics_layer',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7.1,<3.10',
}


setup(**setup_kwargs)
