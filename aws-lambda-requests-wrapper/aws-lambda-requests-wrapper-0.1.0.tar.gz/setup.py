# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['aws_lambda_requests_wrapper']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'aws-lambda-requests-wrapper',
    'version': '0.1.0',
    'description': 'Request/Response wrapper for AWS Lambda with API Gateway',
    'long_description': '# AWS Lambda Requests Wrapper\n\nRequest/Response wrapper for AWS Lambda with API Gateway\n',
    'author': 'rikhilrai',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/DeveloperRSquared/aws-lambda-requests-wrapper',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
