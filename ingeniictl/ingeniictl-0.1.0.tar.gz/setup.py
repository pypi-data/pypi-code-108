# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ingeniictl', 'ingeniictl.cli.infra', 'ingeniictl.logger']

package_data = \
{'': ['*']}

install_requires = \
['typer>=0.4.0,<0.5.0']

entry_points = \
{'console_scripts': ['ingeniictl = ingeniictl.main:app']}

setup_kwargs = {
    'name': 'ingeniictl',
    'version': '0.1.0',
    'description': "Ingenii's Swiss Army Knife",
    'long_description': "# ingeniictl - Ingenii's Swiss Army Knife\n\n- [ingeniictl - Ingenii's Swiss Army Knife](#ingeniictl---ingeniis-swiss-army-knife)\n  - [Overview](#overview)\n  - [Development](#development)\n    - [Makefiles](#makefiles)\n    - [Releasing New Version](#releasing-new-version)\n  - [Install](#install)\n  - [Environment Variables](#environment-variables)\n  - [Executable](#executable)\n  - [Commands](#commands)\n  - [Options](#options)\n\n## Overview\n\nWe have been using Makefiles to help us augument Pulumi with pre/post deployment automation. The goal of this CLI is not to fully replace the Makefiles and the countless targets in there, but to greatly reduce their size.\n\n## Development\n\n1. Launch the Visual Studio Code\n2. Open the project in Dev Container\n3. Congratulations. You have all necessary tools to extend this CLI.\n\n### Makefiles\n\nThere are some handy shortcuts in the makefile.\n\n- `make install` - Installs all dependencies\n- `make build` - Builds the ingeniictl and outputs the `whl` and `zip` files in the `dist` dir.\n- `make publish TOKEN=<pypi token>` - Builds and publishes the ingeniictl to pypi.\n- `make publish-test TOKEN=<pypi token>` - Builds and publishes the ingeniictl to the test pypi.\n- `make test` - Runs tests.\n\n### Releasing New Version\n\n1. Make your changes\n2. Test locally\n3. Bump the package version: `poetry version <patch | minor | major | prepatch | preminor | premajor | rerelease>`\n4. Open a Pull Request (Merge to Releases)\n5. Get someone to review and merge\n6. The CI will automatically publish the new version\n\n## Install\n\n`pip install ingeniictl`\n\n## Environment Variables\n\n`II_LOG_ENABLE_COLORS` - Set to `0` to disable colors in the output messages.  \n`II_LOG_ENABLE_DATETIME_PREFIX` - Set to `0` to disable the date/time prefix in the output messages.\n\n## Executable\n\n```\ningeniictl\n```\n\n## Commands\n\n[infra](./docs/commands/infra.md) - Infrastructure Toolkit\n\n## Options\n```shell\n  --install-completion [bash|zsh|fish|powershell|pwsh]\n                                  Install completion for the specified shell.\n  --show-completion [bash|zsh|fish|powershell|pwsh]\n                                  Show completion for the specified shell, to\n                                  copy it or customize the installation.\n  --help \n```\n",
    'author': 'Teodor Kostadinov',
    'author_email': 'teodor@ingenii.dev',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
