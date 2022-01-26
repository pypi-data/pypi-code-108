# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['pycounts_tat']

package_data = \
{'': ['*']}

install_requires = \
['matplotlib>=3.5.1,<4.0.0']

setup_kwargs = {
    'name': 'pycounts-tat',
    'version': '0.1.1',
    'description': 'Calculate word counts in a text file!',
    'long_description': '# pycounts_tat\n\n[![ci-cd](https://github.com/ttimbers/pycounts_tat/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/ttimbers/pycounts_tat/actions/workflows/ci-cd.yml)\n\nCalculate word counts in a text file!\n\n## Installation\n\n```bash\n$ pip install pycounts_tat\n```\n\n## Usage\n\nTo import the package and check the version:\n\n```\nimport pycounts_tat\n\nprint(pycounts_tat.__version__)\n```\n\n## Contributing\n\nInterested in contributing? Check out the contributing guidelines. Please note that this project is released with a Code of Conduct. By contributing to this project, you agree to abide by its terms.\n\n## License\n\n`pycounts_tat` was created by Monty Python. It is licensed under the terms of the MIT license.\n\n## Credits\n\n`pycounts_tat` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).\n',
    'author': 'Monty Python',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
