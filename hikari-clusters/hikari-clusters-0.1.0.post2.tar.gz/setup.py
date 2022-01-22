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
    'version': '0.1.0.post2',
    'description': 'Tool for clustering with hikari.',
    'long_description': '# hikari-clusters\n[![pypi](https://github.com/TrigonDev/hikari-clusters/actions/workflows/pypi.yml/badge.svg)](https://pypi.org/project/hikari-clusters)\n[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/TrigonDev/hikari-clusters/main.svg)](https://results.pre-commit.ci/latest/github/TrigonDev/hikari-clusters/main)\n\n[Documentation](https://github.com/trigondev/hikari-clusters/wiki) | [CONTRIBUTING.md](https://github.com/trigondev/.github/tree/main/CONTRIBUTING.md)\n\nClustering for hikari made easy. Run examples with `python -m examples.<example name>` (`python -m examples.basic`)\n\nIf you need support, you can contact me `Circuit#3397` after joining [this server](https://discord.gg/dGAzZDaTS9). I don\'t accept friend requests.\n\n<p align="center">\n  <img src="https://us-east-1.tixte.net/uploads/circuit.is-from.space/clustered-bot-structure.jpeg">\n</p>\n\n## Creating Self-Signed Certificate:\n```\nopenssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout cert.key -out cert.cert && cat cert.key cert.cert > cert.pem\n```\n',
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
