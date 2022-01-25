# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['easy_user_input']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'easy-user-input',
    'version': '1.3.0rc2',
    'description': 'Misc python3 methods for collecting input from users',
    'long_description': '# easy-user-input\n### Miscellaneous python3 methods for collecting input from users\n\n#### Includes the following methods:\n- `inputYesNo` for a boolean response\n- `inputChoice` for selecting one option from a list of several\n- `inputStrictString` for a string response containing only allowed characters\n- `inputPath` for a file or directory path, with several options on how to treat existing files\n\n\n#### Links\nPyPI: [https://pypi.org/project/easy-user-input/](https://pypi.org/project/easy-user-input/)\n\nGitHub: [https://github.com/generic-user1/easy-user-input](https://github.com/generic-user1/easy-user-input)\n',
    'author': 'generic-user1',
    'author_email': '89677116+generic-user1@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
