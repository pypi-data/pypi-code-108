# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['hikari_clusters']

package_data = \
{'': ['*']}

install_requires = \
['hikari>=2.0.0.dev105,<3.0.0',
 'pytest-cov>=3.0.0,<4.0.0',
 'websockets>=10.1,<11.0']

setup_kwargs = {
    'name': 'hikari-clusters',
    'version': '0.1.0a7',
    'description': 'Tool for clustering with hikari.',
    'long_description': '# hikari-clusters\n[![pytest](https://github.com/TrigonDev/hikari-clusters/actions/workflows/pytest.yml/badge.svg)](https://github.com/TrigonDev/hikari-clusters/actions/workflows/pytest.yml)\n[![pypi](https://github.com/TrigonDev/hikari-clusters/actions/workflows/pypi.yml/badge.svg)](https://pypi.org/project/hikari-clusters)\n[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/TrigonDev/hikari-clusters/main.svg)](https://results.pre-commit.ci/latest/github/TrigonDev/hikari-clusters/main)\n\n[CONTRIBUTING.md](https://github.com/trigondev/.github/tree/main/CONTRIBUTING.md)\n\nClustering for hikari made easy. Run examples with `python -m examples.<example name>` (`python -m examples.basic`)\n\n<p align="center">\n  <img src="https://us-east-1.tixte.net/uploads/circuit.is-from.space/clustered-bot-structure.jpeg">\n</p>\n\n## Creating Self-Signed Certificate:\n```\nopenssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout cert.key -out cert.cert && cat cert.key cert.cert > cert.pem\n```\n',
    'author': 'Circuit',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/TrigonDev/hikari-clusters',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8.0,<3.11',
}


setup(**setup_kwargs)
