# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': '.'}

packages = \
['cognite', 'cognite.extractorutils.cogex']

package_data = \
{'': ['*']}

install_requires = \
['cognite-extractor-utils>=1.5.3,<2.0.0',
 'requests>=2.26.0,<3.0.0',
 'termcolor>=1.1.0,<2.0.0',
 'toml>=0.10.2,<0.11.0']

entry_points = \
{'console_scripts': ['cogex = cognite.extractorutils.cogex.__main__:main']}

setup_kwargs = {
    'name': 'cognite-extractor-manager',
    'version': '0.2.0',
    'description': 'A project manager for Python based extractors',
    'long_description': '# `cogex`\n\n`cogex` is a tool for managing extractors for Cognite Data Fusion written in Python. It provides\nutilities for initializing a new extractor project and building self-contained executables of Python\nbased extractors.\n\n\n## Important note for users running `pyenv`\n\n`pyenv` is a neat tool for managing Python installations.\n\nSince `cogex` uses PyInstaller to build executables, we need Python to be installed with a shared\ninstance of `libpython`, which `pyenv` does not do by default. To fix this, make sure to add the\n`--enable-shared` flag when installing new Python versions with `pyenv`, like so:\n\n```bash\nenv PYTHON_CONFIGURE_OPTS="--enable-shared" pyenv install 3.9.0\n```\n\nYou can read more about it in the [PyInstaller documentation](https://pyinstaller.readthedocs.io/en/stable/development/venv.html#pyenv-and-pyinstaller)\n\n\n## Overview of features\n\n\n### Start a new extractor project\n\nTo start a new extractor project, move to the desired directory and run\n\n```bash\ncogex init\n```\n\nYou will first be prompted for some information, before `cogex` will initialize a new project.\n\n\n### Add dependencies\n\nExtractor projects initiated with `cogex` will use `poetry` for managing dependencies. Running\n`cogex init` will automatically install the Cognite SDK and extractor-utils framework, but if your\nextractor needs any other dependency, simply add them using `poetry`, like so:\n\n```bash\npoetry add requests\n```\n\n\n### Type checking and code style\n\nIt is recommended that you run code checkers on your extractor, in particular:\n\n * `black` is an opinionated code style checker that will enforce a consistent code style throughout\n   your project. This is useful to avoid unecessary changes and minimizing PR diffs.\n * `isort` is a tool that sorts your imports, also contributing to a consistent code style and\n   minimal PR diffs.\n * `mypy` is a static type checker for Python which ensures that you are not making any type errors\n   in your code that would go unnoticed before suddently breaking your extractor in production.\n\n`cogex` will install all of these, and automatically run them on every commit. If you for some\nreason need to perform a commit despite one of these failing, you can run `git commit --no-verify`,\nalthough this is not recommended.\n\n\n### Build and package an extractor project\n\nIt is not always an option to rely on a Python installation at the machine your extractor will be\ndeployed at. For those scenarios it is useful to package the extractor, including its dependencies\nand the Python runtime, into a single self-contained executable. To do this, run\n\n```bash\ncogex build\n```\n\nThis will create a new executable (for the operating system you ran `cogex build` from) in the\n`dist` directory.\n\n\n### Creating a new version of your extractor\n\nTo keep track of which version of the code base is running at a given deployment it is very useful\nto version your extractor. When releasing a new version, run\n\n```bash\npoetry version [patch/minor/major]\n```\n\nTo automatically bump the corresponding version number. Note that this only updates the version\nnumber in `pyproject.toml`. When running `cogex build` this new version number will be propagated\nthrough the rest of the code base.\n\nAny extractor project should follow semantic versioning, which means you should bump\n\n * `patch` for any minor bug fixes or improvements\n * `minor` for new features or bigger improvements that __doesn\'t__ break compatability\n * `major` for new feature or improvements that breaks compatability with previous versions, in\n   other words for those scenarios where the new version is not a drop-in replacement for an old\n   version. For example:\n   - When adding a new required config field\n   - When removing a config field\n   - When changing defaults in a way that could break existing deployments\n',
    'author': 'Mathias Lohne',
    'author_email': 'mathias.lohne@cognite.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6.1,<4.0.0',
}


setup(**setup_kwargs)
