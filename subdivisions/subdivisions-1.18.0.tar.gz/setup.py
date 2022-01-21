# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['subdivisions', 'subdivisions.builders']

package_data = \
{'': ['*']}

install_requires = \
['arrow',
 'asbool',
 'boto3',
 'coverage',
 'loguru',
 'mypy',
 'python-dotenv',
 'stringcase']

setup_kwargs = {
    'name': 'subdivisions',
    'version': '1.18.0',
    'description': 'A55 AWS PubSub Library',
    'long_description': '# Welcome to Subdivisions\n\n[![PyPI](https://img.shields.io/pypi/v/subdivisions)](https://pypi.org/project/subdivisions/)\n[![Publish](https://github.com/access55/subdivisions/workflows/publish/badge.svg)](https://github.com/access55/subdivisions/actions)\n[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/subdivisions)](https://www.python.org)\n[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow.svg)](https://conventionalcommits.org)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)\n\n[A55 Python library for PubSub Messaging](https://www.youtube.com/watch?v=EYYdQB0mkEU)\n\n### Install in Project\n\n```toml\n# pyproject.toml\n# Add in every project which will\n# receive or send messages\n[tool.subdivisions]\nsource_name = "ProjectName" # ex.: "Client-Manager"\n\n[tool.poetry.dependencies]\nsubdivisions = "*"\n```\nRun `poetry update`\n\n### Usage\n#### Send Messages\n```python\nfrom subdivisions.client import SubClient\nfrom subdivisions.events import UserEvents\n\nclient = SubClient()\nclient.topic = UserEvents.USER_REGISTERED\nclient.send({"foo": "bar"})\n```\n\n#### Receive Messages\n```python\nfrom subdivisions.client import SubClient\nfrom subdivisions.events import UserEvents\n\nclient = SubClient()\nclient.topic = UserEvents.USER_REGISTERED\nmessages = client.get_messages()  # use the ``from_dead_letter=True` to receive Dead Letter messages\n# Process messages\nclient.delete_received_messages()\n```\n\n### Full Configuration options\n\nConfigure subdivisions options in `pyproject.toml` file, inside `[tool.subdivisions]` table:\n\n```toml\n# pyproject.toml\n[tool.subdivisions]\naws_region = "us-east-1"            # AWS Region\naws_allowed_account = ""            # AWS Allowed Account Id for create artifacts / send messages\npub_key = "alias/PubSubKey"         # KMS PubSubKey (must be created first)\nsqs_tags = []                       # SQS tags for new queues. Example [{"foo": "bar"}]\nqueue_prefix = ""                   # Prefix for new SQS queues\nqueue_suffix = ""                   # Suffix for new SQS queues\nqueue_max_receive_count = 1000      # SQS MaxReceiveCount setting\nsns_prefix = ""                     # Prefix for new SNS topics\nsns_suffix = ""                     # Suffix for new SNS topics\nsns_tags = []                       # SNS tags for new topics. Example [{"foo": "bar"}]\nevent_prefix = ""                   # Prefix for new Eventbride rules\nevent_suffix = ""                   # Suffix for new Eventbride rules\nevent_tags = []                     # Eventbridge tags for new rules. Example [{"foo": "bar"}]\nevent_bus = "default"               # Eventbridge Bus\nsource_name = ""                    # Eventbridge default source name. No default, must inform\nauto_create_new_topic = true        # Auto create new topic if not exists in Eventbridge\nauto_remove_from_queue = false      # Acknowledge first messages on receive\nuse_aws_env_vars = true             # Use AWS default env vars. If false append "SUBDIVISION_" on env vars. Example: "SUBDIVISION_AWS_ACCESS_KEY_ID"\ndefault_prefix = "a55"              # Default prefix for all sns, sqs and rule created\ndefault_suffix = ""                 # Default suffix for all sns, sqs and rule created\n```\n\nAll options above can be configured in environment variables. Just append `SUBDIVISIONS_` on name. Example: `SUBDIVISIONS_SOURCE_NAME="my_project"`\n\n### Local Development\n\nFor local development, please first clone and install this project:\n\n```shell\ngit clone git@github.com:access55/subdivisions.git /path/to/project\ncd /path/to/project\n\n# Install on WSL/Linux\nmake install\n\n# Install on Powershell\npoetry install\n```\n\n\n#### Example: Adding a new Topic\nTo avoid different names in different projects for the same topic, (i.e: "client_registered" and\n"customer_registered") please add new events using Python Enum on `subdivisions.event` module:\n\n```python\n# subdivisions.events\nfrom enum import unique, Enum\n\n@unique\nclass MyNewEvents(Enum):\n    MY_NEW_EVENT = "my_new_event"\n```\n\n#### Commit using a conventional commit message\n\nTo generate a new PyPI version, at least one commit must following the\n[Conventional Commit](https://www.conventionalcommits.org/en/v1.0.0/) Specification, when you can\nadd the `feat:` or `fix:` prefix in your message:\n\n```shell\n# Create a new patch event. Ex. 1.0.0 to 1.0.1\ngit commit -m "fix: Event Bug"\n\n# Create a new minor event. Ex. 1.0.0 to 1.1.0\ngit commit -m "feat: Add New Event"\n\n# Create a new major event. Ex. 1.0.0 to 2.0.0\ngit commit -m "feat!: Add New Event \\n\\nBREAKING CHANGE: API changed"\n```\n\nWithout a `feat:` or `fix:` prefixed commited message, code will not generate a new PyPI version.\n\n### Using AWS Credentials locally\n\nSubdivisions will use AWS default environment variables. If you need to define another credentials, use the following variables:\n\n```env\nSUBDIVISIONS_USE_AWS_ENV_VARS="false"\nSUBDIVISIONS_AWS_ACCESS_KEY_ID="your id"\nSUBDIVISIONS_AWS_SECRET_ACCESS_KEY="your key"\nSUBDIVISIONS_AWS_SESSION_TOKEN="your token" # optional\n```\n',
    'author': 'A55 Tech',
    'author_email': 'tech@a55.tech',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/access55/subdivisions',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
