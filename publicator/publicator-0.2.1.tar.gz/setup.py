# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['publicator']

package_data = \
{'': ['*']}

install_requires = \
['colorama>=0.4.4,<0.5.0', 'typer>=0.4.0,<0.5.0']

entry_points = \
{'console_scripts': ['publicator = publicator.cli:app']}

setup_kwargs = {
    'name': 'publicator',
    'version': '0.2.1',
    'description': '',
    'long_description': '# 🗞 Publicator\n\n> A better `poetry publish` experience.\n\n## Features\n\n### Supported\n\n- Ensures you are publishing from your release branch (`main` and `master` by default)\n- Ensures the working directory is clean and latest changes are pulled\n- Reinstalls dependencies to ensure your project works with the latest dependency tree\n- Ensures your Python version is supported by the project and its dependencies\n- Runs the tests\n- Bumps the version in `pyproject.toml` and creates a Git tag based on it\n- Publishes the new version to [Python Package Index](https://pypi.org) or custom repository\n- Pushes commits and tags (newly & previously created) to your Git server\n- See what will be executed with preview mode, without pushing or publishing anything remotely\n\n### Planned\n\n- Open a prefilled GitHub Releases draft after publishing\n\n## Prerequisites\n\n- **Python 3.8** or later\n- **Poetry 1.1** or later\n- **Git 2.11** or later\n\n## Install\n\nInstall with pipx.\n\n```sh\npipx install publicator\n```\n\n## Usage\n\n```plain\nUsage: publicator [OPTIONS] version\n\nArguments:\n  version  can be one of (patch | minor | major | 1.2.3)  [required]\n\nOptions:\n  --repository name               Custom repository for publishing (must be\n                                  specified in pyproject.toml)\n  --any-branch / --no-any-branch  Allow publishing from any branch  [default:\n                                  no-any-branch]\n  --skip-cleaning / --no-skip-cleaning\n                                  Skip repository clean up  [default: no-skip-\n                                  cleaning]\n  --yolo / --no-yolo              Skip reinstall and test steps  [default: no-\n                                  yolo]\n  --skip-tag / --no-skip-tag      Skip creating a new tag  [default: no-skip-\n                                  tag]\n  --skip-publish / --no-skip-publish\n                                  Skip publishing the package to the registry\n                                  [default: no-skip-publish]\n  --skip-push / --no-skip-push    Skip pushing commits and tags to Git\n                                  [default: no-skip-push]\n  --install-completion [bash|zsh|fish|powershell|pwsh]\n                                  Install completion for the specified shell.\n  --show-completion [bash|zsh|fish|powershell|pwsh]\n                                  Show completion for the specified shell, to\n                                  copy it or customize the installation.\n  --help                          Show this message and exit.\n```\n\n## Contributing\n\nSee [**here**](CONTRIBUTING.md) for instructions.\n',
    'author': 'Niko Heikkilä',
    'author_email': 'niko.heikkila@futurice.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8',
}


setup(**setup_kwargs)
