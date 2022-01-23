# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['publicator']

package_data = \
{'': ['*']}

install_requires = \
['mergedeep>=1.3.4,<2.0.0', 'toml>=0.10.2,<0.11.0', 'typer[all]>=0.4.0,<0.5.0']

entry_points = \
{'console_scripts': ['publicator = publicator.cli:app']}

setup_kwargs = {
    'name': 'publicator',
    'version': '0.1.4',
    'description': '',
    'long_description': "# Publicator\n\n> A better `poetry publish`\n\n## Features\n\n### Supported\n\n- Ensures you are publishing from your release branch (main and master by default)\n- Ensures the working directory is clean and that there are no changes not pulled\n- Reinstalls dependencies to ensure your project works with the latest dependency tree\n- Ensures your Python version is supported by the project and its dependencies\n- Runs the tests\n- Bumps the version in pyproject.toml and creates a git tag\n- Publishes the new version to pypi.org\n- Pushes commits and tags (newly & previously created) to your Git server\n\n### Upcoming\n\n- Interactive UI\n- Opens a prefilled GitHub Releases draft after publish\n- See exactly what will be executed with preview mode, without pushing or publishing anything remotely\n\n## Prerequisites\n\n- Python 3.9 or later\n- Poetry 1.1 or later\n- Git 2.11 or later\n\n## Install\n\nInstall with pipx.\n\n```sh\npipx install publicator\n```\n\n## Usage\n\n```plain\n$ publicator --help\n\nUsage:\n\n$ publicator <version>\n\nVersion can be one of:\n    patch | minor | major | 1.2.3\n\nOptions\n    --any-branch            Allow publishing from any branch\n    --branch                Name of the release branch (default: main | master)\n    --no-tests              Skips tests\n    --no-publish            Skips publishing\n    --preview               Show tasks without actually executing them\n    --no-release-draft      Skips opening a GitHub release draft\n    --release-draft-only    Only opens a GitHub release draft\n    --test-script           Name of shell command to run tests before publishing (default: `poetry run pytest`)\n    --message               Version bump commit message. `%s` will be replaced with version. (default: '%s')\n```\n\n## Configuration\n\nTo be added later.\n",
    'author': 'Niko Heikkilä',
    'author_email': 'niko.heikkila@futurice.com',
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
