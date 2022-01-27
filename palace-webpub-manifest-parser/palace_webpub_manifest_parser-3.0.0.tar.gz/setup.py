# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['webpub_manifest_parser',
 'webpub_manifest_parser.core',
 'webpub_manifest_parser.epub',
 'webpub_manifest_parser.odl',
 'webpub_manifest_parser.opds2',
 'webpub_manifest_parser.rwpm']

package_data = \
{'': ['*']}

install_requires = \
['jsonschema>=3.2.0,<4.0.0',
 'multipledispatch>=0.6.0,<0.7.0',
 'pyrsistent==0.16.1',
 'python-dateutil>=2.8.2,<3.0.0',
 'pytz>=2021.1,<2022.0',
 'requests>=2.27.1,<3.0.0',
 'rfc3987>=1.3.8,<2.0.0',
 'uritemplate>=3.0.1,<4.0.0']

setup_kwargs = {
    'name': 'palace-webpub-manifest-parser',
    'version': '3.0.0',
    'description': 'A parser for the Readium Web Publication Manifest, OPDS 2.0 and ODL formats.',
    'long_description': '# webpub manifest parser\n\n[![Run Tests](https://github.com/ThePalaceProject/webpub-manifest-parser/actions/workflows/test.yml/badge.svg)](https://github.com/ThePalaceProject/webpub-manifest-parser/actions/workflows/test.yml)\n[![PyPI](https://img.shields.io/pypi/v/palace-webpub-manifest-parser)](https://pypi.org/project/palace-webpub-manifest-parser/)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)\n[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)\n![Python: 3.7,3.8,3.9,3.10](https://img.shields.io/badge/Python-3.7%20%7C%203.8%20%7C%203.9%20%7C%203.10-blue)\n\nA parser for the\n[Readium Web Publication Manifest (RWPM)](https://github.com/readium/webpub-manifest),\n[Open Publication Distribution System 2.0 (OPDS 2.0)](https://drafts.opds.io/opds-2.0), and\n[Open Distribution to Libraries 1.0 (ODL)](https://drafts.opds.io/odl-1.0.html) formats.\n\n## Usage\n\nInstall the library with `pip`\n\n```bash\npip install palace-webpub-manifest-parser\n```\n\n### Pyenv\n\nYou can optionally install the python version to run the library with using pyenv.\n\n1. Install [pyenv](https://github.com/pyenv/pyenv#installation)\n\n2. Install one of the supported Python versions:\n    ```bash\n    pyenv install <python-version>\n    ```\n\n3. Install [pyenv-virtualenv](https://github.com/pyenv/pyenv-virtualenv#installation) plugin\n\n4. Create a virtual environment:\n    ```bash\n    pyenv virtualenv <virtual-env-name>\n    pyenv activate <virtual-env-name>\n    ```\n\n5. Install the library\n    ```bash\n    pip install palace-webpub-manifest-parser\n    ```\n\n## Setting up a development environment\n\n### Running tests using tox\n\n1. Make sure that a virtual environment is not activated and deactivate it if needed:\n    ```bash\n    deactivate\n    ```\n\n2. Install `tox` and `tox-pyenv` globally:\n    ```bash\n    pip install tox tox-pyenv\n    ```\n\n3. Make your code prettier using isort and black:\n    ```bash\n    pre-commit run -a\n    ```\n\n4. To run the unit tests use the following command:\n    ```bash\n    tox -e <python-version>\n    ```\n    where `<python-version>` is one of supported python versions:\n   - py37\n   - py38\n   - py39\n   - py310\n\n    For example, to run the unit test using Python 3.9 run the following command:\n    ```bash\n    tox -e py39\n    ```\n\n## Releasing\n\nReleases will be automatically published to PyPI when new releases are created on github by the\n[release.yml](.github/workflows/release.yml) workflow. Just create a release in github with the version\nnumber that you would like to use as the tag, and the rest will happen automatically.\n',
    'author': 'The Palace Project',
    'author_email': 'info@thepalaceproject.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ThePalaceProject/webpub-manifest-parser',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4',
}


setup(**setup_kwargs)
