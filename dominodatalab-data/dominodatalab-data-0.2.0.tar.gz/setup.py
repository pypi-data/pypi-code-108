# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['datasource_api_client',
 'datasource_api_client.api',
 'datasource_api_client.api.datasource',
 'datasource_api_client.api.proxy',
 'datasource_api_client.models',
 'domino_data',
 'domino_data.training_sets',
 'training_set_api_client',
 'training_set_api_client.api',
 'training_set_api_client.api.default',
 'training_set_api_client.models']

package_data = \
{'': ['*']}

install_requires = \
['attrs>=20.1.0,<22.0.0',
 'backoff>=1.11.1,<2.0.0',
 'httpx>=0.15.4,<0.19.0',
 'loguru>=0.5.3,<0.6.0',
 'pandas>=1.3.0',
 'pyarrow>=5.0.0,<6.0.0',
 'python-dateutil>=2.8.0,<3.0.0']

setup_kwargs = {
    'name': 'dominodatalab-data',
    'version': '0.2.0',
    'description': 'Domino Data API for interacting with Domino Data features',
    'long_description': '# Domino Data API\n\n<div align="center">\n\n[![Build status](https://github.com/dominodatalab/domino-data/workflows/build/badge.svg?branch=master&event=push)](https://github.com/dominodatalab/domino-data/actions?query=workflow%3Abuild)\n[![Python Version](https://img.shields.io/pypi/pyversions/dominodatalab-data.svg)](https://pypi.org/project/dominodatalab-data/)\n[![Dependencies Status](https://img.shields.io/badge/dependencies-up%20to%20date-brightgreen.svg)](https://github.com/dominodatalab/domino-data/pulls?utf8=%E2%9C%93&q=is%3Apr%20author%3Aapp%2Fdependabot)\n\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![Security: bandit](https://img.shields.io/badge/security-bandit-green.svg)](https://github.com/PyCQA/bandit)\n[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/dominodatalab/domino-data/blob/master/.pre-commit-config.yaml)\n[![Semantic Versions](https://img.shields.io/badge/%20%20%F0%9F%93%A6%F0%9F%9A%80-semantic--versions-e10079.svg)](https://github.com/dominodatalab/domino-data/releases)\n[![License](https://img.shields.io/github/license/dominodatalab/domino-data)](https://github.com/dominodatalab/domino-data/blob/master/LICENSE)\n\nDomino Data API for interacting with Access Data features\n\n</div>\n\n## Installation\n\n```bash\npip install -U dominodatalab-data\n```\n\nor install with `Poetry`\n\n```bash\npoetry add dominodatalab-data\n```\n\n### Makefile usage\n\n[`Makefile`](https://github.com/dominodatalab/domino-data/blob/master/Makefile) contains a lot of functions for faster development.\n\n<details>\n<summary>1. Download and remove Poetry</summary>\n<p>\n\nTo download and install Poetry run:\n\n```bash\nmake poetry-download\n```\n\nTo uninstall\n\n```bash\nmake poetry-remove\n```\n\n</p>\n</details>\n\n<details>\n<summary>2. Install all dependencies and pre-commit hooks</summary>\n<p>\n\nInstall requirements:\n\n```bash\nmake install\n```\n\nPre-commit hooks coulb be installed after `git init` via\n\n```bash\nmake pre-commit-install\n```\n\n</p>\n</details>\n\n<details>\n<summary>3. Codestyle</summary>\n<p>\n\nAutomatic formatting uses `pyupgrade`, `isort` and `black`.\n\n```bash\nmake codestyle\n\n# or use synonym\nmake formatting\n```\n\nCodestyle checks only, without rewriting files:\n\n```bash\nmake check-codestyle\n```\n\n> Note: `check-codestyle` uses `isort`, `black` and `darglint` library\n\n<details>\n<summary>4. Code security</summary>\n<p>\n\n```bash\nmake check-safety\n```\n\nThis command launches `Poetry` integrity checks as well as identifies security issues with `Safety` and `Bandit`.\n\n```bash\nmake check-safety\n```\n\n</p>\n</details>\n\n</p>\n</details>\n\n<details>\n<summary>5. Type checks</summary>\n<p>\n\nRun `mypy` static type checker\n\n```bash\nmake mypy\n```\n\n</p>\n</details>\n\n<details>\n<summary>6. Tests</summary>\n<p>\n\nRun `pytest`\n\n```bash\nmake test\n```\n\n</p>\n</details>\n\n<details>\n<summary>7. All linters</summary>\n<p>\n\nOf course there is a command to ~~rule~~ run all linters in one:\n\n```bash\nmake lint\n```\n\nthe same as:\n\n```bash\nmake test && make check-codestyle && make mypy && make check-safety\n```\n\n</p>\n</details>\n\n<details>\n<summary>8. Cleanup</summary>\n<p>\n\nDelete pycache files\n\n```bash\nmake pycache-remove\n```\n\nRemove package build\n\n```bash\nmake build-remove\n```\n\nOr to remove pycache and build:\n\n```bash\nmake clean-all\n```\n\n</p>\n</details>\n\n<details>\n<summary>9. Docs</summary>\n<p>\n\nBuild the documentation\n\n```bash\nmake docs\n```\n\nOpen the docs index page\n\n```bash\nmake open-docs\n```\n\n</p>\n</details>\n\n## 📈 Releases\n\nYou can see the list of available releases on the [GitHub Releases](https://github.com/dominodatalab/domino-data/releases) page.\n\nWe follow [Semantic Versions](https://semver.org/) specification.\n\nWe use [`Release Drafter`](https://github.com/marketplace/actions/release-drafter). As pull requests are merged, a draft release is kept up-to-date listing the changes, ready to publish when you’re ready. With the categories option, you can categorize pull requests in release notes using labels.\n\n### List of labels and corresponding titles\n\n|               **Label**               |  **Title in Releases**  |\n| :-----------------------------------: | :---------------------: |\n|       `enhancement`, `feature`        |       🚀 Features       |\n| `bug`, `refactoring`, `bugfix`, `fix` | 🔧 Fixes & Refactoring  |\n|       `build`, `ci`, `testing`        | 📦 Build System & CI/CD |\n|              `breaking`               |   💥 Breaking Changes   |\n|            `documentation`            |    📝 Documentation     |\n|            `dependencies`             | ⬆️ Dependencies updates |\n\nYou can update it in [`release-drafter.yml`](https://github.com/dominodatalab/domino-data/blob/master/.github/release-drafter.yml).\n\nGitHub creates the `bug`, `enhancement`, and `documentation` labels for you. Dependabot creates the `dependencies` label. Create the remaining labels on the Issues tab of your GitHub repository, when you need them.\n\n## 🛡 License\n\n[![License](https://img.shields.io/github/license/dominodatalab/domino-data)](https://github.com/dominodatalab/domino-data/blob/master/LICENSE)\n\nThis project is licensed under the terms of the `Apache Software License 2.0` license. See [LICENSE](https://github.com/dominodatalab/domino-data/blob/master/LICENSE) for more details.\n\n## 📃 Citation\n\n```bibtex\n@misc{dominodatalab-data,\n  author = {dominodatalab},\n  title = {Domino Data API for interacting with Access Data features},\n  year = {2021},\n  publisher = {GitHub},\n  journal = {GitHub repository},\n  howpublished = {\\url{https://github.com/dominodatalab/domino-data}}\n}\n```\n\n## Credits [![🚀 Your next Python package needs a bleeding-edge project structure.](https://img.shields.io/badge/python--package--template-%F0%9F%9A%80-brightgreen)](https://github.com/TezRomacH/python-package-template)\n\nThis project was generated with [`python-package-template`](https://github.com/TezRomacH/python-package-template)\n',
    'author': 'Aaron Read',
    'author_email': 'aaron.read@dominodatalab.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/dominodatalab/domino-data',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
