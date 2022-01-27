# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['rasa_sdk', 'rasa_sdk.cli', 'rasa_sdk.knowledge_base']

package_data = \
{'': ['*']}

install_requires = \
['Sanic-Cors>=1.0.0,<2.0.0',
 'coloredlogs>=10,<16',
 'prompt-toolkit>=2.0,<3.0',
 'requests>=2.23,<3.0',
 'sanic>=21.6.0,<22.0.0',
 'typing-extensions>=3.7.4,<4.0.0',
 'urllib3>=1.26.5,<2.0.0']

extras_require = \
{':sys_platform != "win32"': ['uvloop<0.15.0']}

setup_kwargs = {
    'name': 'rasa-sdk',
    'version': '3.0.4',
    'description': 'Open source machine learning framework to automate text- and voice-based conversations: NLU, dialogue management, connect to Slack, Facebook, and more - Create chatbots and voice assistants',
    'long_description': '# Rasa Python-SDK\n[![Join the chat on Rasa Community Forum](https://img.shields.io/badge/forum-join%20discussions-brightgreen.svg)](https://forum.rasa.com/?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)\n[![Build Status](https://github.com/RasaHQ/rasa-sdk/workflows/Continous%20Integration/badge.svg?event=push)](https://github.com/RasaHQ/rasa-sdk/actions/runs/)\n[![Coverage Status](https://coveralls.io/repos/github/RasaHQ/rasa-sdk/badge.svg?branch=main)](https://coveralls.io/github/RasaHQ/rasa-sdk?branch=main)\n[![PyPI version](https://img.shields.io/pypi/v/rasa-sdk.svg)](https://pypi.python.org/pypi/rasa-sdk)\n[![Documentation Status](https://img.shields.io/badge/docs-stable-brightgreen.svg)](https://rasa.com/docs)\n\nPython SDK for the development of custom actions for Rasa.\n\n## Installation\n\nTo install the SDK run\n\n```bash\npip install rasa-sdk\n```\n\n## Compatibility\n\n`rasa-sdk` package:\n\n| SDK version    | compatible Rasa version           |\n|----------------|-----------------------------------|\n| `1.0.x`        | `>=1.0.x`                         |\n\nold `rasa_core_sdk` package:\n\n| SDK version    | compatible Rasa Core version           |\n|----------------|----------------------------------------|\n| `0.12.x`       | `>=0.12.x`                             |\n| `0.11.x`       | `0.11.x`                               |\n| not compatible | `<=0.10.x`                             |\n\n## Usage\n\nDetailed instructions can be found in the Rasa Documentation about\n[Custom Actions](https://rasa.com/docs/rasa/core/actions).\n\n## Docker\n\n### Usage\n\nIn order to start an action server using implemented custom actions,\nyou can use the available Docker image `rasa/rasa-sdk`.\n\nBefore starting the action server ensure that the folder containing\nyour actions is handled as Python module and therefore has to contain\na file called `__init__.py`\n\nThen start the action server using:\n\n```bash\ndocker run -p 5055:5055 --mount type=bind,source=<ABSOLUTE_PATH_TO_YOUR_ACTIONS>,target=/app/actions \\\n\trasa/rasa-sdk:<version>\n```\n\nThe action server is then available at `http://localhost:5055/webhook`.\n\n### Custom Dependencies\n\nTo add custom dependencies you enhance the given Docker image, e.g.:\n\n```\n# Extend the official Rasa SDK image\nFROM rasa/rasa-sdk:<version>\n\n# Change back to root user to install dependencies\nUSER root\n\n# To install system dependencies\nRUN apt-get update -qq && \\\n    apt-get install -y <NAME_OF_REQUIRED_PACKAGE> && \\\n    apt-get clean && \\\n    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*\n\n# To install packages from PyPI\nRUN pip install --no-cache-dir <A_REQUIRED_PACKAGE_ON_PYPI>\n\n# Switch back to non-root to run code\nUSER 1001\n```\n\n\n## Building from source\n\nRasa SDK uses Poetry for packaging and dependency management. If you want to build it from source,\nyou have to install Poetry first. This is how it can be done:\n\n```\ncurl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python3\n```\n\nThere are several other ways to install Poetry. Please, follow \n[the official guide](https://python-poetry.org/docs/#installation) to see all possible options.\n\nTo install dependencies and `rasa-sdk` itself in editable mode execute\n```\nmake install\n```\n\n## Code Style\n\nTo ensure a standardized code style we use the formatter [black](https://github.com/ambv/black).\nIf your code is not formatted properly, GitHub CI will fail to build.\n\nIf you want to automatically format your code on every commit, you can use [pre-commit](https://pre-commit.com/).\nJust install it via `pip install pre-commit` and execute `pre-commit install`.\n\nTo check and reformat files execute\n```\nmake lint\n```\n\n## Steps to release a new version\nReleasing a new version is quite simple, as the packages are build and distributed \nby GitHub Actions.\n\n*Release steps*:\n1. Switch to the branch you want to cut the release from (`main` in case of a \n  major / minor, the current release branch for patch releases).\n2. Run `make release`\n3. Create a PR against main or the release branch (e.g. `1.2.x`)\n4. Once your PR is merged, tag a new release (this SHOULD always happen on \n  `main` or release branches), e.g. using\n    ```bash\n    git tag 1.2.0 -m "next release"\n    git push origin 1.2.0\n    ```\n    GitHub Actions will build this tag and push a package to \n    [pypi](https://pypi.python.org/pypi/rasa-sdk).\n5. **If this is a minor release**, a new release branch should be created \n  pointing to the same commit as the tag to allow for future patch releases, \n  e.g.\n    ```bash\n    git checkout -b 1.2.x\n    git push origin 1.2.x\n    ```\n\n## License\nLicensed under the Apache License, Version 2.0. Copyright 2021 Rasa\nTechnologies GmbH. [Copy of the license](LICENSE.txt).\n\nA list of the Licenses of the dependencies of the project can be found at\nthe bottom of the\n[Libraries Summary](https://libraries.io/github/RasaHQ/rasa-sdk).\n',
    'author': 'Rasa Technologies GmbH',
    'author_email': 'hi@rasa.com',
    'maintainer': 'Tom Bocklisch',
    'maintainer_email': 'tom@rasa.com',
    'url': 'https://rasa.com',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<3.10',
}


setup(**setup_kwargs)
