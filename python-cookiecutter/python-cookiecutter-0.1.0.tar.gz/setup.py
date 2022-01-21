# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['python_cookiecutter']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.0.3,<9.0.0',
 'desert>=2020.11.18,<2021.0.0',
 'marshmallow>=3.14.1,<4.0.0',
 'requests>=2.27.1,<3.0.0']

entry_points = \
{'console_scripts': ['python-cookiecutter = python_cookiecutter.console:main']}

setup_kwargs = {
    'name': 'python-cookiecutter',
    'version': '0.1.0',
    'description': 'The hypermodern Python project',
    'long_description': "# Hypermodern Python Guide\n\n[![Tests](https://github.com/udeepam/python-cookiecutter/workflows/Tests/badge.svg)](https://github.com/udeepam/python-cookiecutter/actions?workflow=Tests)\n[![Codecov](https://codecov.io/gh/udeepam/python-cookiecutter/branch/master/graph/badge.svg)](https://codecov.io/gh/udeepam/python-cookiecutter)\n[![PyPI](https://img.shields.io/pypi/v/python-cookiecutter.svg)](https://pypi.org/project/python-cookiecutter/)\n\nThis repository follows the series of articles for [hypermodern python](https://cjolowicz.github.io/posts/hypermodern-python-01-setup/).\n\nWhat is used:\n* Package, dependency, and environment manager: `conda`\n* Package and dependency manager: `poetry`\n* Package manager: `pip`\n* Continuous integration: `GitHub Actions`\n* Command-line interface: `click`\n* Managing git hooks: `pre-commit`\n* Data validation: `desert`, `marshmallow`\n* Testing:\n  * Unit testing: `pytest`\n  * Test automation: `nox`\n  * Security audit: `Safety`\n  * Code coverage: `Coverage.py`\n  * Coverage reporting: `codecov`\n* Documentation:\n  * Check documentation examples: `xdoctest`\n  * Documentation: `sphinx`\n  * Generate API documentation: `autodoc`, `napoleon`, `sphinx-autodoc-typehints`\n* Linting:\n  * `flake8`:\n    * `flake8-black`: generates warnings if it detects Black would reformat a source file.\n    * `flake8-import-order`: generates warnings if import statements are not grouped and ordered in a consistent and PEP 8-compliant way.\n    * `flake8-bugbear`: helps you find various bugs and design problems in your programs.\n    * `flake8-bandit`: find common security issues in Python code.\n    * `flake8-annotations`: detects the absence of type annotations for functions, helping you keep track of unannotated code.\n    * `flake8-docstrings`: uses the tool pydocstyle to check that docstrings are compliant with the style recommendations of PEP 257.\n  * `mypy`: static type checking.\n  * `pytype`: static type checking.\n  * `typeguard`: runtime type checking.\n  * `darglint`: checks that docstring descriptions match function definitions.\n* Formatting:\n  * `black`: modifies conflicting files.\n\n## Instructions not in the articles.\n1. Clone the repository.\n2. Create a new conda environment:\n   ```bash\n   conda env create -f environment.yml\n   ```\n3. Download `Coverage.py` using `zsh` cli:\n   ```bash\n   poetry add --dev 'coverage[toml]' pytest-cov\n   ```\n",
    'author': 'udeepam',
    'author_email': 'udeepa652@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/udeepam/python-cookiecutter',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
