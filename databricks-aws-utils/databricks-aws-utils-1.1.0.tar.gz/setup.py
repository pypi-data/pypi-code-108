# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['databricks_aws_utils']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'databricks-aws-utils',
    'version': '1.1.0',
    'description': 'Databricks AWS Utils',
    'long_description': '# Databricks AWS Utils\n\nDatabricks AWS Utils is a library to abstract Databricks integration with AWS Services\n\n## Features\n\n- Convert Delta Table to be consumed by AWS Athena with Schema evolution\n- Run queries against AWS RDS using AWS Secrets Manager to retrive the connection properties and returns as Spark DataFrame\n\n## Install\n\n`pip install databricks-aws-utils`\n\n## Contributing\n\n- See our [Contributing Guide](CONTRIBUTING.md)\n\n## Change Log\n\n- See our [Change Log](CHANGELOG.md)\n',
    'author': 'Lucas Vieira',
    'author_email': 'lucas.vieira94@outlook.com',
    'maintainer': 'Lucas Vieira',
    'maintainer_email': 'lucas.vieira94@outlook.com',
    'url': 'https://github.com/lucasvieirasilva/databricks-aws-utils',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<3.10',
}


setup(**setup_kwargs)
