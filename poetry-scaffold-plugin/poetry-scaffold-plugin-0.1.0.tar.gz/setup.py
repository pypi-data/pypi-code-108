# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['poetry_scaffold_plugin']

package_data = \
{'': ['*'], 'poetry_scaffold_plugin': ['templates/*']}

install_requires = \
['cleo>=1.0.0a4,<2.0.0', 'poetry>=1.2.0a2,<2.0.0', 'tomlkit>=0.8.0,<0.9.0']

entry_points = \
{'poetry.application.plugin': ['scaffold = '
                               'poetry_scaffold_plugin.plugins:ScaffoldPlugin']}

setup_kwargs = {
    'name': 'poetry-scaffold-plugin',
    'version': '0.1.0',
    'description': "Poetry plugin that installs and configures dev dependencies, so you don't have to.",
    'long_description': '# poetry-scaffold-plugin\n\nA Poetry plugin that installs and configures default dev dependencies, so you don\'t have to.\n\nGet nice tools. Avoid the tedious boilerplate of setting up a project.\n\nv0.1.0 is a preview and relies on the preview of Poetry\'s new plugin system. Expect rough edges.\n\n## Requirements\n\n- Poetry 1.2 (preview)\n\nPoetry will add support for plugins in v1.2, currently in preview. To try poetry-scaffold-plugin, you must install Poetry >=1.2.0a2\n\nUpdating from Poetry v1.1 to the preview can\'t be done via Poetry\'s `self update`. Instead, use the new Poetry installer script. See the [master version of the installer docs](https://python-poetry.org/docs/master/#installation) for more information. (Don\'t use the v1.1 docs, which refer to the old installer.)\n\n## Installation\n\nAfter installing the Poetry preview, the new `poetry plugin` commands will be available. To install the plugin:\n\n```bash\n$ poetry plugin add poetry-scaffold-plugin\n```\n\n**Note:** Poetry plugins are installed in your global Poetry environment, not the project environment.\n\n## Usage\n\n```bash\n$ poetry new my-project && cd my-project\n$ poetry scaffold\n```\n\nPoetry\'s built-in `poetry new` provides a standard project layout. poetry-scaffold-plugin\'s `poetry scaffold` provides the dev dependencies and configuration.\n\nThere are no customisable settings in v0.1.0. Your project\'s configuration can be tweaked in the usual way, by modifying pyproject.toml, setup.cfg and pre-commit-config.yaml.\n\n## What you get\n\nThe packages and configuration in poetry-scaffold-plugin were inspired by, but diverge from, Claudio Jolowicz\'s series on [Hypermodern Python](https://cjolowicz.github.io/posts/hypermodern-python-01-setup/).\n\n- Testing\n    - [pytest](https://docs.pytest.org/) for testing\n    - [coverage](https://coverage.readthedocs.io/) measures test coverage and identifies untested lines of code\n    - [pytest-cov](https://pytest-cov.readthedocs.io/) adds nice coverage reports to pytest output\n    - [pytest-mock](https://github.com/pytest-dev/pytest-mock/) makes it more convenient to use mocks (e.g. adds a mocker fixture)\n    - [hypothesis](https://hypothesis.readthedocs.io/) helps find edge cases that break your code\n- Linting and formatting\n    - [black](https://black.readthedocs.io/) formats your code\n    - [isort](https://pycqa.github.io/isort/) sorts import statements\n    - [flake8](https://flake8.pycqa.org/) catches common mistakes and suggests good Python practices\n    - [flake8-bugbear](https://github.com/PyCQA/flake8-bugbear) catches even more issues\n    - [mypy](https://mypy.readthedocs.io/) checks type annotations\n    - [semgrep](https://github.com/returntocorp/semgrep) looks for common security problems\n    - [pre-commit](https://pre-commit.com/) runs checks (and automatically fixes what it can) before committing\n- Niceties\n    - [pdbpp](https://github.com/pdbpp/pdbpp) works like the standard pdb debugger but has extra features like "sticky" mode\n    - [ipython](https://ipython.readthedocs.io/) provides a nicer shell for those interactive experimentation sessions\n\nThe linting is especially opinionated. If it\'s too much, or clashes with your house style, try deleting B9 from the extend-select section in setup.cfg.\n\nThe mypy settings are more lenient. The pre-commit hook will check type annotations that you\'ve added, but won\'t demand you use type annotations.',
    'author': 'Ellen Potter',
    'author_email': '38250543+ellen364@users.noreply.github.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
