# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['delfino', 'delfino.click_utils', 'delfino.commands', 'delfino.models']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.0.3,<9.0.0', 'pydantic>=1.8.2,<2.0.0', 'toml>=0.10.2,<0.11.0']

extras_require = \
{':python_version < "3.8"': ['importlib-metadata'],
 'all': ['black',
         'isort',
         'pre-commit',
         'pytest',
         'coverage',
         'pytest-cov',
         'mypy',
         'pylint',
         'pycodestyle',
         'pydocstyle',
         'twine',
         'shellingham'],
 'completion': ['shellingham'],
 'format': ['black', 'isort', 'pre-commit'],
 'lint': ['pylint', 'pycodestyle', 'pydocstyle'],
 'test': ['pytest', 'coverage', 'pytest-cov'],
 'typecheck': ['mypy'],
 'upload_to_pypi': ['twine'],
 'verify_all': ['black',
                'isort',
                'pre-commit',
                'pytest',
                'coverage',
                'pytest-cov',
                'mypy',
                'pylint',
                'pycodestyle',
                'pydocstyle']}

entry_points = \
{'console_scripts': ['delfino = delfino.main:main', 'mike = delfino.main:main']}

setup_kwargs = {
    'name': 'delfino',
    'version': '0.12.0',
    'description': 'A collection of command line helper scripts wrapping tools used during Python development.',
    'long_description': '<h1 align="center" style="border-bottom: none;">🧰&nbsp;&nbsp;Delfino&nbsp;&nbsp;🧰</h1>\n<h3 align="center">A collection of command line helper scripts wrapping tools used during Python development.</h3>\n\n<p align="center">\n    <a href="https://app.circleci.com/pipelines/github/radeklat/delfino?branch=main">\n        <img alt="CircleCI" src="https://img.shields.io/circleci/build/github/radeklat/delfino">\n    </a>\n    <a href="https://app.codecov.io/gh/radeklat/delfino/">\n        <img alt="Codecov" src="https://img.shields.io/codecov/c/github/radeklat/delfino">\n    </a>\n    <a href="https://github.com/radeklat/delfino/tags">\n        <img alt="GitHub tag (latest SemVer)" src="https://img.shields.io/github/tag/radeklat/delfino">\n    </a>\n    <img alt="Maintenance" src="https://img.shields.io/maintenance/yes/2021">\n    <a href="https://github.com/radeklat/delfino/commits/main">\n        <img alt="GitHub last commit" src="https://img.shields.io/github/last-commit/radeklat/delfino">\n    </a>\n</p>\n\n<!--\n    How to generate TOC from PyCharm:\n    https://github.com/vsch/idea-multimarkdown/wiki/Table-of-Contents-Extension\n-->\n[TOC levels=1,2 markdown formatted bullet hierarchy]: # "Table of content"\n\n# Table of content\n- [Installation](#installation)\n  - [Optional dependencies](#optional-dependencies)\n- [Usage](#usage)\n  - [Auto-completion](#auto-completion)\n- [Development](#development)\n  - [Minimal plugin](#minimal-plugin)\n\n# Installation\n\n- pip: `pip install delfino[all]`\n- Poetry: `poetry add -D delfino[all]`\n- Pipenv: `pipenv install -d delfino[all]`\n\n## Optional dependencies\n\nEach project may use different sub-set of commands. Therefore, dependencies of all commands are optional and checked only when the command is executed.\n\nUsing `[all]` installs all the [optional dependencies](https://setuptools.pypa.io/en/latest/userguide/dependency_management.html#optional-dependencies) used by all the built-in commands. If you want only a sub-set of those dependencies, there are finer-grained groups available:\n\n- For top-level parameters:\n  - `completion` - for `--show-completion` and `--install-completion`\n- For individual commands (matches the command names):\n  - `upload_to_pypi`\n  - `build_docker`\n  - `typecheck`\n  - `format`\n- For groups of commands:\n  - `test` - for testing and coverage commands\n  - `lint` - for all the linting commands\n- For groups of groups:\n  - `verify_all` - same as `[typecheck,format,test,lint]`\n  - `all` - all optional packages\n\n## Configuration\n\nDelfino will assume certain project structure. However, you can customize it to match your own by overriding the default values in the `pyproject.toml` file. Here are the defaults that you can modify:\n\n```toml\n[tool.delfino]\nreports_directory = "reports"\nsources_directory = "src"\ntests_directory = "tests"\ntest_types = ["unit", "integration"]\ndisable_commands = []\n\n[tool.delfino.dockerhub]\nusername = ""\nbuild_for_platforms = [\n    "linux/amd64",\n    "linux/arm64",\n    "linux/arm/v7",\n]\n```\n\n# Usage\n\nRun `delfino --help` to see all available commands and their usage.\n\n## Auto-completion\n\nYou can either attempt to install completions automatically with:\n\n```shell script\ndelfino --install-completion\n```\n\nor generate it with:\n\n```shell script\ndelfino --show-completion\n```\n\nand manually put it in the relevant RC file.\n\nThe auto-completion implementation is dynamic so that every time it is invoked, it uses the current project. Each project can have different plugins or disable certain commands it doesn\'t use. And dynamic auto-completion makes sure only the currently available commands will be suggested.\n\nThe downside of this approach is that evaluating what is available each time is slower than a static list of commands.\n\n# Development\n\nDelfino is a simple wrapper around [Click](https://click.palletsprojects.com). It allows you to add custom, project-specific [commands](https://click.palletsprojects.com/en/8.0.x/quickstart/#basic-concepts-creating-a-command). Let\'s call them plugins. Plugins are expected in the root of the project, in a Python package called `commands`. Any sub-class of [`click.Command`](https://click.palletsprojects.com/en/8.0.x/api/#click.Command) in any `.py` file in this folder will be automatically used by Delfino.\n\n## Minimal plugin\n\n<!-- TODO(Radek): Delfino expects `pyproject.toml` configured. -->\n<!-- TODO(Radek): Delfino expects Poetry or Pipenv to be available. -->\n\n1. Create the `commands` package:\n   ```shell script\n   mkdir commands\n   touch commands/__init__.py\n   ```\n2. Create a file `commands/plugin_test.py`, with the following content:\n   ```python\n   import click\n   \n   @click.command()\n   def plugin_test():\n       """Tests commands placed in the `commands` folder are loaded."""\n       print("✨ This plugin works! ✨")\n   ```\n3. See if Delfino loads the plugin. Open a terminal and in the root of the project, call: `delfino --help`. You should see something like this:\n   ```text\n   Usage: delfino [OPTIONS] COMMAND [ARGS]...\n   \n   Options:\n     --help  Show this message and exit.\n   \n   Commands:\n     ...\n     plugin-test            Tests commands placed in the `commands` folder...\n     ...\n   ```\n4. Run the plugin with `delfino plugin-test`\n\n<!--\n## Advanced plugin\n\nDelfino adds optional bits of functionality on top of Click. The following example demonstrates some of those:\n\n```python\nimport click\n\nfrom delfino.contexts import pass_app_context, AppContext\nfrom delfino.validation import assert_pip_package_installed, pyproject_toml_key_missing\n\n@click.command()\n# The `pass_app_context` decorator adds `AppContext` as the first parameter.\n@pass_app_context\ndef plugin_test(app_context: AppContext):\n   """Tests commands placed in the `commands` folder are loaded."""\n   # Test optional dependencies. Any failing assertion will be printed as:\n   # Command \'<NAME>\' is misconfigured. <ASSERTION ERROR MESSAGE> \n   assert_pip_package_installed("delfino")\n   \n   # AppContext contain a parsed `pyproject.toml` file.\n   # Plugins can add their config under `[tool.delfino.plugins.<PLUGIN_NAME>]`.\n   assert "plugin_test" in app_context.pyproject_toml.tool.delfino.plugins, \\\n       pyproject_toml_key_missing("tool.delfino.plugins.plugin_test")\n   \n   print(app_context.pyproject_toml.tool.delfino.plugins["plugin-test"])\n```\n-->',
    'author': 'Radek Lát',
    'author_email': 'radek.lat@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/radeklat/delfino',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7.0,<4.0.0',
}


setup(**setup_kwargs)
