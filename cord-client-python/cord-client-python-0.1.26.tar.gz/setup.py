# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cord',
 'cord.constants',
 'cord.http',
 'cord.orm',
 'cord.project_ontology',
 'cord.utilities']

package_data = \
{'': ['*']}

install_requires = \
['cryptography>=3.4.8,<4.0.0',
 'python-dateutil>=2.8.2,<3.0.0',
 'requests==2.25.0',
 'tqdm>=4.32.1,<5.0.0',
 'uuid>=1.30,<2.0']

setup_kwargs = {
    'name': 'cord-client-python',
    'version': '0.1.26',
    'description': 'Cord Python SDK Client',
    'long_description': '<h1 align="center">\n  <p align="center">Cord Python API Client</p>\n  <a href="https://cord.tech"><img src="https://app.cord.tech/CordLogo.svg" width="150" alt="Cord logo"/></a>\n</h1>\n\n[![license](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)\n\n***Where the world creates and manages training data***\n\n## 💻 Features\n\n- Minimal low-level Python client that allows you to interact with Cord\'s API\n- Supports Python: `3.6`, `3.7`, and `3.8`\n\n## ✨ Relevant Links\n* [Cord website](https://cord.tech)\n* [Cord web app](https://app.cord.tech)\n* [Cord documentation](https://docs.cord.tech)\n\n## 💡 Getting Started\n\nFor full documentation, visit [Cord Python API Client](https://docs.cord.tech/docs/client/).\n\nFirst, install Cord Python API Client using the [pip](https://pip.pypa.io/en/stable/installing) package manager:\n\n```bash\npip install cord-client-python\n```\n\nThen, create an API key for authentication via the [Cord web app](https://app.cord.tech). Pass the project ID and API key as environment variables or pass them explicitly when you initialise the CordClient object.\n\n```bash\nexport CORD_PROJECT_ID="<project_id>"\nexport CORD_API_KEY="<project_api_key>"\n```\n\nPassing the project ID and API key as environment variables, you can initialise the Cord client directly.\n\n```python\nfrom cord.client import CordClient\n\nclient = CordClient.initialise()\n```\n\nIf you want to avoid setting environment variables, you can initialise the Cord client by passing the project ID and API key as strings.\n\n```python\nfrom cord.client import CordClient\n\nclient = CordClient.initialise("<resource_id>", "<resource_api_key>")\n```\n\nIf you wish to instantiate several client objects and avoid passing parameters each time, you can instantiate a CordConfig object, pass the project ID and API key as strings, and initialise the client with the config object.\n\n```py\nfrom cord.client import CordClient\nfrom cord.client import CordConfig\n\nconfig = CordConfig("<resource_id>", "<resource_api_key>")\nclient = CordClient.initialise_with_config(config)\n```\n\nOnce you have instantiated a Cord client, it is easy to fetch information associated with the given project ID.\n\n```py\nfrom cord.client import CordClient\n\nclient = CordClient.initialise()\nproject = client.get_project()\n```\n\n## 🐛 Troubleshooting\n\nPlease report bugs to [GitHub Issues](https://github.com/cord-team/cord-client-python/issues). Just make sure you read the [Cord documentation](https://docs.cord.tech) and search for related issues first.\n',
    'author': 'Cord Technologies Limited',
    'author_email': 'hello@cord.tech',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/cord-team/cord-client-python',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
