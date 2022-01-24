# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['gitlab_ps_utils']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.25.1,<3.0.0', 'tqdm>=4.61.0,<5.0.0', 'xmltodict>=0.12.0,<0.13.0']

setup_kwargs = {
    'name': 'gitlab-ps-utils',
    'version': '0.5.0',
    'description': 'Shared python utilities used by GitLab Professional Services tooling',
    'long_description': '# GitLab PS Utils\n\nGitLab PS utils is the foundational API and utilities libraries used by GitLab Professional Services. \nTo see the source code, project backlog and contributing guide, [check here](https://gitlab.com/gitlab-org/professional-services-automation/gitlab-ps-utils)\n\n## Install\n\n```bash\npip install gitlab-ps-utils\n```\n\n## Usage\n\nThis library contains various utility modules and classes.\nRefer to the repository source code to see available utility functions.\n\n### Importing a utility function\n\n```python\nfrom gitlab_ps_utils.string_utils import strip_numbers\n\ntest_var = "abc123"\nprint(strip_numbers(test_var))\n```\n\n### Importing a utility class\n\n```python\nfrom gitlab_ps_utils.api import GitLabApi\n\ngl_api = GitLabApi()\n\ngl_api.generate_get_request("http://gitlab.example.com", "token", "/projects")\n```\n\n## Other resources\n\n### Python-GitLab\n\nWe include a basic GitLab API wrapper class in this library. We will include specific API wrapper functions in the future.\nOur wrapper class and specific wrappers were created when [python-gitlab](https://python-gitlab.readthedocs.io/en/stable/) was in a much earlier state,\nso we continued to use our wrapper instead of switching to python-gitlab\n\nFor generic requests to the GitLab API, our wrapper is more lightweight than python-gitlab,\nbut python-gitlab is a great option for more complex API scripts\n\n',
    'author': 'GitLab Professional Services',
    'author_email': 'proserv@gitlab.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/gitlab-org/professional-services-automation/gitlab-ps-utils',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8.0',
}


setup(**setup_kwargs)
