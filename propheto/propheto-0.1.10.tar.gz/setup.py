# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['propheto',
 'propheto.deployments',
 'propheto.deployments.aws',
 'propheto.deployments.azure',
 'propheto.deployments.gcp',
 'propheto.model_frameworks',
 'propheto.package',
 'propheto.package.templates.api',
 'propheto.package.templates.api.v1',
 'propheto.package.templates.api.v1.endpoints',
 'propheto.project',
 'propheto.project.configuration',
 'propheto.tracking']

package_data = \
{'': ['*']}

install_requires = \
['boto3>=1.17.105,<2.0.0',
 'cloudpickle>=1.6.0,<2.0.0',
 'pydantic>=1.8.2,<2.0.0',
 'requests>=2.25.1,<3.0.0',
 'tqdm>=4.61.1,<5.0.0',
 'troposphere>=3.0.1,<4.0.0']

setup_kwargs = {
    'name': 'propheto',
    'version': '0.1.10',
    'description': 'Propheto - MLOps Software Platform',
    'long_description': '<div align="center">\n\n<img src="https://docs.getpropheto.com/logo-light.svg">\n\n<p align="center">\n  <a href="https://getpropheto.com/">Website</a> •\n  <a href="https://docs.getpropheto.com/">Docs</a>\n</p>\n\n[![PyPI - Propheto Version](https://img.shields.io/pypi/v/zenml.svg?label=pip&logo=PyPI&logoColor=white)](https://pypi.org/project/propheto/)\n[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/propheto)](https://pypi.org/project/propheto/)\n[![PyPI Status](https://pepy.tech/badge/propheto)](https://pepy.tech/project/propheto)\n![GitHub](https://img.shields.io/github/license/propheto-io/propheto)\n\n</div>\n\n\n# Propheto - Open ML Platform \n\n## Overview\n\nPropheto is a flexible, high-performance framework for deploying, managing, and monitoring models. Using Propheto, data scientists can quickly and easily deploy their models as complete, fully functioning microservices. Propheto allows:\n\n- Integration first to support all major data systems, ML frameworks, amd MLOps tools\n- No vendor lock in so you can use all the tools and systems your team needs\n- Real-time or batch prediction endpoints with minimal overhead and maximum parallelism\n- Easy debugging, testing, and versioning for model pipelines\n- Security first architecture with portability across cloud and on-prem environments\n- Open-core but designed for enterprise (automated logging, monitoring, and documentation)\n\nWith only a few simple commands in their IDE (jupyter notebooks, VS Code, Pycharm, etc.) data scientists can deploy models in their cloud architecture with all of the logging, tracking, scaling, and reporting required.\n\nThe Propheto package works with all major system architectures so that it can easily integrate into the production data and software applications and can easily be managed by other DevOps or software engineering resources. However, Propheto also makes it such that data scientists can self-manage these resources without any burden and without working through these other teams.\n\nReady to get started? checkout our [Quickstart guide](https://docs.getpropheto.com/quickstart/) or [sample notebook](https://github.com/Propheto-io/propheto/blob/main/docs/Propheto%20Iris%20Classification.ipynb) to see Propheto in action.\n\n\n## Installation\nPropheto is hosted on [pypi](https://pypi.org/project/propheto/) and can be installed by simply using `pip`\n\n```sh\npip install propheto\n```\n\n## Get in Touch\nThere are several ways to get in touch with us:\n\n* Open an issue at: https://github.com/Propheto-op/propheto \n* Email us at: hello@propheto.io\n\n## Contributing\nThanks so much for your interest in supporting our project. We welcome any contributions to Propheto. We will be putting together a contribution guide but in the meantime please feel free to reach out to us or submit PRs as you see fit.\n\n## License\nPropheto is licensed under Apache 2.0',
    'author': 'Dan McDade',
    'author_email': 'dan@propheto.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Propheto-io/propheto',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
