# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['testpackagemds']

package_data = \
{'': ['*']}

install_requires = \
['matplotlib>=3.5.0,<4.0.0']

setup_kwargs = {
    'name': 'testpackagemds',
    'version': '0.4.2',
    'description': 'Calculate words  in a text file!',
    'long_description': '# testpackagemds \n\n\n[![codecov](https://codecov.io/gh/flor14/testpackagemds/branch/main/graph/badge.svg)](https://codecov.io/gh/flor14/testpackagemds)\n\n\n\nA package created to try a GitHub Actions workflow! :)\n\n\n[![ci-cd](https://github.com/flor14/testpackagemds/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/flor14/testpackagemds/actions/workflows/ci-cd.yml)\n\nA package created to try a GitHub Actions workflow!\n\n\n## Installation\n\n```bash\n$ pip install testpackagemds\n```\n\n## Usage\n\n\n\n## Contributing\n\nInterested in contributing? Check out the contributing guidelines. Please note that this project is released with a Code of Conduct. By contributing to this project, you agree to abide by its terms.\n\n\n\n\n',
    'author': 'Florencia',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
