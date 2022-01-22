# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['gitlab_ci_cd_variables_tree']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.0.3,<9.0.0', 'python-gitlab>=3.1.0,<4.0.0', 'rich>=11.0.0,<12.0.0']

entry_points = \
{'console_scripts': ['gitlab-ci-cd-variables-tree = '
                     'gitlab_ci_cd_variables_tree.cli:main']}

setup_kwargs = {
    'name': 'gitlab-ci-cd-variables-tree',
    'version': '0.1.0',
    'description': 'Show Gitlab CI/CD variables as Tree structure',
    'long_description': "# gitlab-ci-cd-variables-tree [![PyPi version](https://img.shields.io/pypi/v/gitlab-ci-cd-variables-tree.svg)](https://pypi.python.org/pypi/gitlab-ci-cd-variables-tree/) [![PyPI pyversions](https://img.shields.io/pypi/pyversions/gitlab-ci-cd-variables-tree.svg)](https://pypi.python.org/pypi/gitlab-ci-cd-variables-tree/) [![](https://img.shields.io/github/license/f9n/gitlab-ci-cd-variables-tree.svg)](https://github.com/f9n/gitlab-ci-cd-variables-tree/blob/master/LICENSE)\n\nShow [Gitlab](https://gitlab.com) CI/CD variables as Tree structure\n\n## Installation\n\n```\n$ # Install\n$ python3 -m pip install gitlab-ci-cd-variables-tree --user\n\n$ # Install with upgrade\n$ python3 -m pip install gitlab-ci-cd-variables-tree --user --upgrade\n```\n\n## Usage\n\nFirst you need to create a personal token on [gitlab.com](https://gitlab.com). [Link](https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html#create-a-personal-access-token\n)\n\n```bash\n$ gitlab-ci-cd-variables-tree --help\n\n$ # Show version\n$ gitlab-ci-cd-variables-tree version\ngitlab-ci-cd-variables-tree: 0.1.0\n\n$ # Show gitlab ci-cd variables,\n$ # Make sure that the 'GITLAB_URL' and 'GITLAB_TOKEN' environment variable is set.\n$ export GITLAB_URL=https://gitlab.com\n$ export GITLAB_TOKEN=<YOUR_PRIVATE_TOKEN>\n\n$ gitlab-ci-cd-variables-tree show --gitlab-group-id 6161\n\n$ # Show with detailed log messages\n$ gitlab-ci-cd-variables-tree --log-level INFO show --gitlab-group-id 6161\n\n```\n",
    'author': 'Fatih Sarhan',
    'author_email': 'f9n@protonmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/f9n/gitlab-ci-cd-variables-tree',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
