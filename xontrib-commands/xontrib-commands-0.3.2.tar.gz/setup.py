# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['xontrib', 'xontrib_commands']

package_data = \
{'': ['*']}

install_requires = \
['python-dotenv>=0.19.1,<0.20.0']

extras_require = \
{':python_version >= "3.6" and python_version < "4.0"': ['xonsh>=0.10.1',
                                                         'arger>=1.2.7,<2.0.0',
                                                         'rich']}

setup_kwargs = {
    'name': 'xontrib-commands',
    'version': '0.3.2',
    'description': 'Useful xonsh-shell commands/alias functions',
    'long_description': '<p align="center">\nUseful xonsh-shell commands/alias/completer functions\n</p>\n\n## Installation\n\nTo install use pip:\n\n``` bash\nxpip install xontrib-commands\n# or: xpip install -U git+https://github.com/jnoortheen/xontrib-commands\n```\n\n## Usage\n\n``` bash\nxontrib load commands\n```\n\n## building alias\n\nUse [`xontrib_commands.Command`](https://github.com/jnoortheen/xontrib-commands/blob/main/xontrib/commands.py#L9) \nto build [arger](https://github.com/jnoortheen/arger) dispatcher\nfor your functions.\n\n```py\nfrom xontrib_commands import Command\n@Command.reg\ndef record_stats(pkg_name=".", path=".local/stats.txt"):\n    stat = $(scc @(pkg_name))\n    echo @($(date) + stat) | tee -a @(path)\n```\n\nNow a full CLI is ready\n```sh\n$ record-stats --help                                                                        \nusage: xonsh [-h] [-p PKG_NAME] [-a PATH]\n\noptional arguments:\n  -h, --help            show this help message and exit\n  -p PKG_NAME, --pkg-name PKG_NAME\n  -a PATH, --path PATH\n```\n\n## Commands\n\n- The following commands are available once the xontrib is loaded.\n\n### 1. reload-mods\n\n```\nusage: reload-mods [-h] name\n\nReload any python module in the current xonsh session.\nHelpful during development.\n\npositional arguments:\n  name        Name of the module/package to reload. Giving partial names matches all the nested modules.\n\noptional arguments:\n  -h, --help  show this help message and exit\n\nExamples\n-------\n$ reload-mods xontrib\n    - this will reload all modules imported that starts with xontrib name\n\nNotes\n-----\n    Please use\n        `import module` or `import module as mdl` patterns\n    Using\n        `from module import name`\n        will not reload the name imported\n\n```  \n          \n\n### 2. report-key-bindings\n\n```\nusage: report-key-bindings [-h]\n\nShow current Prompt-toolkit bindings in a nice table format\n\noptional arguments:\n  -h, --help  show this help message and exit\n\n```  \n          \n\n### 3. dev\n\n```\ndev v1.0.0 (nuclear v1.1.10) - A command to cd into a directory. (Default action)\n\nUsage:\ndev [COMMAND] [OPTIONS] [NAME]\n\nArguments:\n   [NAME] - name of the folder to cd into. This searches for names under $PROJECT_PATHS or the ones registered with ``dev add``\n\nOptions:\n  --help [SUBCOMMANDS...] - Display this help and exit\n\nCommands:\n  add           - Register the current folder to dev command.\n                  When using this, it will get saved in a file, also that is used during completions.\n  ls            - Show currently registered paths\n  load-env FILE - Load environment variables from the given file into Xonsh session\n                  \n                  Using https://github.com/theskumar/python-dotenv\n\nRun "dev COMMAND --help" for more information on a command.\n\n```  \n          \n',
    'author': 'Noortheen Raja NJ',
    'author_email': 'jnoortheen@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/jnoortheen/xontrib-commands',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6',
}


setup(**setup_kwargs)
