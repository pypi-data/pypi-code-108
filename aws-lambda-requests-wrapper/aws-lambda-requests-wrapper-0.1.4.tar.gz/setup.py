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
    'version': '0.1.4',
    'description': 'Request/Response wrapper for AWS Lambda with API Gateway',
    'long_description': '# AWS Lambda Requests Wrapper\n\nRequest/Response wrapper for AWS Lambda with API Gateway\n\n[![Build](https://github.com/DeveloperRSquared/aws-lambda-requests-wrapper/actions/workflows/build.yaml/badge.svg)](https://github.com/DeveloperRSquared/aws-lambda-requests-wrapper/actions/workflows/build.yaml)\n[![Deploy](https://github.com/DeveloperRSquared/aws-lambda-requests-wrapper/actions/workflows/deploy.yaml/badge.svg)](https://github.com/DeveloperRSquared/aws-lambda-requests-wrapper/actions/workflows/deploy.yaml)\n\n[![Python 3.7+](https://img.shields.io/badge/python-3.7+-brightgreen.svg)](#aws-lambda-requests-wrapper)\n[![PyPI - License](https://img.shields.io/pypi/l/aws-lambda-requests-wrapper.svg)](LICENSE)\n[![PyPI - Version](https://img.shields.io/pypi/v/aws-lambda-requests-wrapper.svg)](https://pypi.org/project/aws-lambda-requests-wrapper)\n\n[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)\n\n## Setup\n\n```sh\npoetry install\npre-commit install\npre-commit run --all-files\n```\n\n## Contributing\n\nContributions are welcome via pull requests.\n\n## Issues\n\nIf you encounter any problems, please file an\n[issue](https://github.com/DeveloperRSquared/aws-lambda-requests-wrapper/issues) along with a\ndetailed description.\n',
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
