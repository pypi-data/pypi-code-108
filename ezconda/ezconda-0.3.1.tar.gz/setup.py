# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ezconda', 'ezconda.experimental']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=5.4.1,<6.0.0', 'rich>=10.11.0,<11.0.0', 'typer[all]>=0.4.0,<0.5.0']

entry_points = \
{'console_scripts': ['ezconda = ezconda.main:app']}

setup_kwargs = {
    'name': 'ezconda',
    'version': '0.3.1',
    'description': 'Create, Manage, Re-create conda environments & specifications with ease.',
    'long_description': '# EZconda\n\n![EZconda](https://github.com/SarthakJariwala/ezconda/blob/2945291bc9ef123cb52e9c6436906ac0728b0451/docs/logo.png)\n\n<p align="center">\n    <a href="https://github.com/SarthakJariwala/ezconda/actions?workflow=Tests">\n        <img src="https://github.com/SarthakJariwala/ezconda/workflows/Tests/badge.svg">\n    </a>\n    <a href="https://codecov.io/gh/SarthakJariwala/ezconda">\n        <img src="https://codecov.io/gh/SarthakJariwala/ezconda/branch/main/graph/badge.svg">\n    </a>\n    <a href="https://anaconda.org/conda-forge/ezconda">\n        <img alt="Conda (channel only)" src="https://img.shields.io/conda/vn/conda-forge/ezconda">\n    </a>\n    <a href="https://ezconda.sarthakjariwala.com">\n        <img src="https://github.com/SarthakJariwala/ezconda/workflows/Docs/badge.svg">\n    </a>\n</p>\n\n<p align="center">\n    <em><b>Create, Manage, Re-create</b> conda environments & specifications with ease.</em>\n</p>\n\n---\n\n**EZconda** is a command line interface application that helps practitioners create and manage `conda` environment and related specifications with ease.\n\n## Key Features\n\n- **Environment specifications** : Add & remove packages from the <abbr title="commonly known as environment.yml file">specifications file</abbr> as you install & remove packages. _**No manual file edits!**_\n\n- **Environment management** : Create & manage `conda` environments with ease.\n\n- **Reproducible environments** : Lock current environment state and re-create it when necessary.\n\n- **Easy to use & intuitive** : It very closely mimics `conda` API, so there is no new API to learn for users. Autocomplete for all shells.\n\n- **Fast & Reliable Environment resolution** : Get fast and reliable environment solves by default. *EZconda* uses `mamba` by default, but you can easily switch between `mamba` and `conda`.\n\n- **Best practices built-in** : Enforces the user to follow best `conda` practices.\n\n## Requirements\n\n- [Conda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html) installation\n\n## Installation\n\nThe recommended way to install **EZconda** is using `conda` or `mamba` in the `base` environment : \n\n### Using `conda`: \n\n```console\n$ conda install ezconda -c conda-forge -n base\n```\n\n### Using `mamba`:\n\n```console\n$ mamba install ezconda -c conda-forge -n base\n```\n\n## Contributing Guidelines\n\n<!-- TODO Add contributing guidelines -->\n\n### Run tests\n\n```bash\ndocker-compose up --build test\n```\n\n### Local iterative development\n\n```bash\ndocker-compose build dev && docker-compose run dev bash\n```',
    'author': 'Sarthak Jariwala',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
