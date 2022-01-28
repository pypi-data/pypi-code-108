# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['openqlab',
 'openqlab.analysis',
 'openqlab.conversion',
 'openqlab.io',
 'openqlab.io.importers',
 'openqlab.io.importers._old_importers',
 'openqlab.plots']

package_data = \
{'': ['*']}

install_requires = \
['importlib-metadata>=4.0,<5.0',
 'matplotlib>=3.2.1,<4.0.0',
 'numpy>=1.18,<2.0',
 'pandas>=1.3,<2.0',
 'pyserial>=3.5,<4.0',
 'scipy>=1.5,<2.0',
 'tabulate>=0.8.9,<0.9.0',
 'typeguard>=2.9.1,<3.0.0',
 'wcwidth>=0.2.5,<0.3.0']

extras_require = \
{'hdf': ['tables>=3.6.1,<4.0.0'],
 'visa': ['pyvisa-py>=0.5.1,<0.6.0', 'PyVISA>=1.11.1,<2.0.0']}

setup_kwargs = {
    'name': 'openqlab',
    'version': '0.4.0',
    'description': 'An open-source collection of tools for quantum-optics experiments',
    'long_description': '# openqlab\n\n[![pipeline status](https://gitlab.com/las-nq/openqlab/badges/master/pipeline.svg)](https://gitlab.com/las-nq/openqlab/commits/master)\n[![coverage report](https://gitlab.com/las-nq/openqlab/badges/master/coverage.svg)](https://gitlab.com/las-nq/openqlab/commits/master)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n\n\n`openqlab` provides a collection of useful tools and helpers for the\nanalysis of lab data in the Nonlinear Quantum Optics Group at the University\nof Hamburg.\n\nPart of the content in this package was written during the PhD theses of\nSebastian Steinlechner and Tobias Gehring. It is currently maintained by\nSebastian Steinlechner, Christian Darsow-Fromm, Jan Petermann and is looking for more\nvolunteers who would like to contribute.\n\nRead the latest changes in our [changelog](CHANGELOG.md).\n\n## Documentation\n\n* Current documentation of the [latest release](https://las-nq-serv.physnet.uni-hamburg.de/python/openqlab)\n* Current documentation of the [latest development version](https://las-nq-serv.physnet.uni-hamburg.de/python/openqlab-stage)\n\n## Features\n\n* Importers for various file formats:\n  * Agilent/Keysight scopes (binary and CSV)\n  * Rohde & Schwarz spectrum analyzers\n  * Tektronix spectrum analyzer\n  * plain ascii\n  * and a few more...\n* easily create standard plots from measurement data\n* design control loops\n* analyze beam profiler data\n* generate covariance matrices for N partite systems\n* several postprocessing functions for entanglement data\n* analyse and automatically plot squeezing data\n* tools for working with dB units\n\n## Installation\n\nFor a detailed installation instruction see the main [documentation](https://las-nq-serv.physnet.uni-hamburg.de/python/openqlab/).\n\n## Usage\n\nYou will need an up-to-date Python 3 environment to use this package, e.g.\nthe Anaconda Python distribution will work just fine. Please refer to the\n`requirements.txt` for a list of prerequisites (although these should be\ninstalled automatically, if necessary).\n\nFor examples and details on how to use this package, please refer to the\ndocumentation.\n\n## Development\n\n### Poetry\nUse [Poetry](https://python-poetry.org/) to manage the development packages.\nIf you are missing a small how-to, just ask and write it. :)\n\n```bash\npoetry install\n```\n\n### Tests\nPlease write unittests if you add new features.\nThe structure for the test should represent the structure of the package itself.\nEach subpackage should have its own folder prefixed with `test_` and should contain subfolders with the same structure.\nEvery `.py` file (module) should be represented by one folder containing test files that test specific functions of that file.\nFor example:\n- `tests`\n    - `test_subpackage1`\n        - `test_module1`\n            - `test_function1_of_module1.py`\n            - `test_function2_of_module1.py`\n        - `test_module2`\n            - `test_function1_of_module2.py`\n            - `test_function2_of_module2.py`\n    - `test_subpackage2`\n\nFor very simple classes or modules, the whole module can be tested in one `test_module.py` file but may still be contained inside a folder with the same name.\nAll tests located in `src/test/*` are automatically tested when pushing to Gitlab.\n\nTo run them manually use:\n```bash\nmake test\n```\n\n### Code Formatter\n\nWe use [`pre-commit`](https://pre-commit.com/#python) for automatic code formatting before committing.\nIt is automatically installed with the development packages.\nThe command to enable the hooks is:\n```bash\npre-commit install\n```\n\n### Changelog\n\nPlease write every change that seems significant in the [CHANGELOG.md](CHANGELOG.md) file.\n\n### Release a new version\n\n#### 1. Use poetry to change the version number\n```bash\npoetry version patch  # small fixes\npoetry version minor  # small features\npoetry version major  # breaking changes\n```\n\n#### 2. Edit the changelog\n\nChange the headline of `[unreleased]` and use the version name.\n\n#### 3. Merge it to Master\n\nFrom the `master` branch the deployment process will finish it automatically.\n\n----\n(c) 2020, LasNQ @ Uni Hamburg\n',
    'author': 'Jan Petermann',
    'author_email': 'jpeterma@physnet.uni-hamburg.de',
    'maintainer': 'Christian Darsow-Fromm',
    'maintainer_email': 'cdarsowf@physnet.uni-hamburg.de',
    'url': 'https://gitlab.com/las-nq/openqlab',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7.1,<3.11',
}


setup(**setup_kwargs)
