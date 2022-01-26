# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['aws_lambda_typing',
 'aws_lambda_typing.common',
 'aws_lambda_typing.context',
 'aws_lambda_typing.events',
 'aws_lambda_typing.responses']

package_data = \
{'': ['*']}

extras_require = \
{':python_version < "3.8"': ['typing-extensions>=4.0.1,<5.0.0']}

setup_kwargs = {
    'name': 'aws-lambda-typing',
    'version': '2.9.10',
    'description': 'A package that provides type hints for AWS Lambda event, context and response objects',
    'long_description': "# AWS Lambda Typing\n\n![build](https://github.com/MousaZeidBaker/aws-lambda-typing/workflows/Publish/badge.svg)\n![test](https://github.com/MousaZeidBaker/aws-lambda-typing/workflows/Test/badge.svg)\n[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)\n![python_version](https://img.shields.io/badge/python-%3E=3.6-blue.svg)\n[![pypi_v](https://img.shields.io/pypi/v/aws-lambda-typing)](https://pypi.org/project/aws-lambda-typing)\n[![pypi_dm](https://img.shields.io/pypi/dm/aws-lambda-typing)](https://pypi.org/project/aws-lambda-typing)\n\nA package that provides type hints for AWS Lambda event, context and response\nobjects. It's a convenient way to get autocomplete and type hints built into\nIDEs. Type annotations are not checked at runtime but are only enforced by third\nparty tools such as type checkers, IDEs, linters, etc.\n\n##### Table of Contents\n- [Usage](#usage)\n- [Demo](#demo)\n- [Types](#types)\n  - [Context](#context)\n  - [Events](#events)\n  - [Responses](#responses)\n- [Test](#test)\n- [Contributing](#contributing)\n- [Issues](#issues)\n\n## Usage\n### Example: AWS SQS event\n\n```python\nfrom aws_lambda_typing import context as context_, events\n\n\ndef handler(event: events.SQSEvent, context: context_.Context) -> None:\n    for record in event['Records']:\n        print(record['body'])\n\n    print(context.get_remaining_time_in_millis())\n\n    message: events.sqs.SQSMessage\n\n```\n\n## Demo\n### IDE autocomplete\n![ide_autocomplete](https://raw.githubusercontent.com/MousaZeidBaker/aws-lambda-typing/master/media/ide_autocomplete.gif)\n\n### IDE code reference information\n![code_reference_information](https://raw.githubusercontent.com/MousaZeidBaker/aws-lambda-typing/master/media/code_reference_information.gif)\n\n## Types\n### Context\n- Context\n\n### Events\n- ALBEvent\n- APIGatewayRequestAuthorizerEvent\n- APIGatewayTokenAuthorizerEvent\n- APIGatewayProxyEventV1\n- APIGatewayProxyEventV2\n- AppSyncResolverEvent\n- CloudFormationCustomResourceEvent\n- CloudWatchEventsMessageEvent\n- CloudWatchLogsEvent\n- CodeCommitMessageEvent\n- CodePipelineEvent\n- ConfigEvent\n- DynamoDBStreamEvent\n- IoTPreProvisioningHookEvent\n- KinesisFirehoseEvent\n- KinesisStreamEvent\n- MQEvent\n- MSKEvent\n- S3Event\n- S3BatchEvent\n- SecretsManagerRotationEvent\n- SESEvent\n- SNSEvent\n- SQSEvent\n\n### Responses\n- ALBResponse\n- APIGatewayAuthorizerResponse\n- APIGatewayProxyResponseV1\n- APIGatewayProxyResponseV2\n- IoTPreProvisioningHookResponse\n- S3BatchResponse\n\n### Other\n- PolicyDocument\n\n## Develop\nActivate virtual environment\n```shell\npoetry shell\n```\n\nInstall dependencies\n```shell\npoetry install --remove-untracked\n```\n\nInstall git hooks\n```shell\npre-commit install --hook-type pre-commit\n```\n\nRun tests\n```shell\nmypy tests\n```\n\nRun linter\n```shell\nflake8 .\n```\n\nFormat code\n```shell\nblack .\n```\n\nSort imports\n```shell\nisort .\n```\n\n## Contributing\nContributions are welcome via pull requests.\n\n## Issues\nIf you encounter any problems, please file an\n[issue](https://github.com/MousaZeidBaker/aws-lambda-typing/issues) along with a\ndetailed description.\n",
    'author': 'Mousa Zeid Baker',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/MousaZeidBaker/aws-lambda-typing',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'extras_require': extras_require,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
