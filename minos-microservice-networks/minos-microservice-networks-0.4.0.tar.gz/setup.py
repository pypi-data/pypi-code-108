# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['minos',
 'minos.networks',
 'minos.networks.brokers',
 'minos.networks.brokers.collections',
 'minos.networks.brokers.collections.queues',
 'minos.networks.brokers.dispatchers',
 'minos.networks.brokers.handlers',
 'minos.networks.brokers.messages',
 'minos.networks.brokers.messages.models',
 'minos.networks.brokers.publishers',
 'minos.networks.brokers.publishers.queued',
 'minos.networks.brokers.publishers.queued.queues',
 'minos.networks.brokers.subscribers',
 'minos.networks.brokers.subscribers.queued',
 'minos.networks.brokers.subscribers.queued.queues',
 'minos.networks.decorators',
 'minos.networks.decorators.callables',
 'minos.networks.decorators.definitions',
 'minos.networks.discovery',
 'minos.networks.discovery.clients',
 'minos.networks.requests',
 'minos.networks.rest',
 'minos.networks.scheduling']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.7.4,<4.0.0',
 'aiokafka>=0.7.0,<0.8.0',
 'aiomisc>=14.0.3,<15.0.0',
 'aiopg>=1.2.1,<2.0.0',
 'crontab>=0.23.0,<0.24.0',
 'dependency-injector>=4.32.2,<5.0.0',
 'minos-microservice-common>=0.4.0,<0.5.0',
 'orjson>=3.6.5,<4.0.0']

setup_kwargs = {
    'name': 'minos-microservice-networks',
    'version': '0.4.0',
    'description': 'Python Package with the common network classes and utilities used in Minos Microservice.',
    'long_description': "# Minos Microservice Network\n\n[![codecov](https://codecov.io/gh/Clariteia/minos_microservice_networks/branch/main/graph/badge.svg)](https://codecov.io/gh/Clariteia/minos_microservice_networks)\n![Tests](https://github.com/Clariteia/minos_microservice_networks/actions/workflows/python-tests.yml/badge.svg)\n\nMinos is a framework which helps you create [reactive](https://www.reactivemanifesto.org/) microservices in Python.\nInternally, it leverages Event Sourcing, CQRS and a message driven architecture to fulfil the commitments of an\nasynchronous environment.\n\n## Documentation\n\nThe official documentation as well as the API you can find it under https://clariteia.github.io/minos_microservice_networks/. \nPlease, submit any issue regarding documentation as well!\n\n## Set up a development environment\n\nMinos uses `poetry` as its default package manager. Please refer to the\n[Poetry installation guide](https://python-poetry.org/docs/#installation) for instructions on how to install it.\n\nNow you con install all the dependencies by running\n```bash\nmake install\n```\n\nIn order to make the pre-commits checks available to git, run\n```bash\npre-commit install\n```\n\nMake yourself sure you are able to run the tests. Refer to the appropriate section in this guide.\n\n## Run the tests\n\nIn order to run the tests, please make sure you have the [Docker Engine](https://docs.docker.com/engine/install/)\nand [Docker Compose](https://docs.docker.com/compose/install/) installed.\n\nMove into `tests/` directory\n\n```bash\ncd tests/\n```\nRun service dependencies:\n\n```bash\ndocker-compose up -d\n```\n\nInstall library dependencies:\n\n```bash\nmake install\n```\n\nRun tests:\n\n```bash\nmake test\n```\n\n## How to contribute\n\nMinos being an open-source project, we are looking forward to having your contributions. No matter whether it is a pull\nrequest with new features, or the creation of an issue related to a bug you have found.\n\nPlease consider these guidelines before you submit any modification.\n\n### Create an issue\n\n1. If you happen to find a bug, please file a new issue filling the 'Bug report' template.\n2. Set the appropriate labels, so we can categorise it easily.\n3. Wait for any core developer's feedback on it.\n\n### Submit a Pull Request\n\n1. Create an issue following the previous steps.\n2. Fork the project.\n3. Push your changes to a local branch.\n4. Run the tests!\n5. Submit a pull request from your fork's branch.\n\n## Credits\n\nThis package was created with ![Cookiecutter](https://github.com/audreyr/cookiecutter) and the ![Minos Package](https://github.com/Clariteia/minos-pypackage) project template.\n\n",
    'author': 'Minos Framework Devs',
    'author_email': 'hey@minos.run',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'http://www.minos.run/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
