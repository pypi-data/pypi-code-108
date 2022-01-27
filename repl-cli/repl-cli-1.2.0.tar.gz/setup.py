# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['repl_cli']

package_data = \
{'': ['*']}

install_requires = \
['replit[all]>=3.1.0,<4.0.0',
 'requests[all]>=2.25.1,<3.0.0',
 'snow-pyrepl[all]>=0.50,<0.51',
 'typer[all]>=0.3.2,<0.4.0',
 'watchdog[all]>=2.1.5,<3.0.0']

entry_points = \
{'console_scripts': ['replit = repl_cli.main:app']}

setup_kwargs = {
    'name': 'repl-cli',
    'version': '1.2.0',
    'description': '',
    'long_description': "# Replit CLI\n![logo](https://sjcdn.is-a.dev/file/ravjqk)\n\n```\npip install repl-cli\n```\nWelcome to Replit CLI! With the Replit CLI Application, you can work with your repls locally, including clone, pull, and push, the core features of the CLI. The full list of features includes-\n\n```\nPS C:\\> replit\nUsage: replit [OPTIONS] COMMAND [ARGS]...\n\nOptions:\n  --install-completion [bash|zsh|fish|powershell|pwsh]\n\t\t\t\t\t\t\t\t  Install completion for the specified shell.\n  --show-completion [bash|zsh|fish|powershell|pwsh]\n\t\t\t\t\t\t\t\t  Show completion for the specified shell, to\n\t\t\t\t\t\t\t\t  copy it or customize the installation.\n\n  --help                          Show this message and exit.\n\nCommands:\n  clone    Clone a Repl's contents to your local machine\n  db       Edit the Replit DB for a Repl\n  env      Interact with the Environment of the Repl of the Current Working...\n  exec     Execute a command to run on the remote repl.\n  login    Authenticate with Replit CLI.\n  pull     Pull the remote contents of the repl inside the working...\n  push     Push changes to the server and override remote.\n  run      Run, Stop, or Restart a Repl from your local machine.\n  shell    Connect to a bash shell with a remote repl.\n  user     Lookup the details for a Replit User\n  version  Output the current version for Replit CLI\nPS C:\\>\n```\n\n## Installation\n- Make sure you have Python 3.6 or higher installed. To do so, type `python` inside of a Command Prompt/Terminal instance. If you have Python installed, a Python shell will come up with the version number. (type ` quit() ` inside of the python shell to quit it) If you do not have Python 3.6+ or do not have Python at all, you can install it by downloading the installer for your platform located [here](https://www.python.org/downloads/)\n- Once you have python, run the following command- ` pip install repl-cli `, preferably with Administrator access (Unix platforms do not need admin access, and `Run as Administrator` on Windows) to make sure that your PC recognizes Replit CLI properly. \n- Once installed, type `replit` into a shell to get started!\n\n## Documentation\nTo see the docs and for more information, click [here](https://replitcli.repl.co)\n\n## Building From Source\nTo build from source, run the following commands-\n```\ngit clone https://github.com/CoolCoderSJ/Replit-CLI.git\ncd .\\replit-cli\\replit_cli\npython main.py\n```\n\n## Credits\nThanks to the many people who helped grow this project-\n- @Codemonkey51 and @turbio for help with Crosis, the Replit API\n- @SpotandJake for help with the JS server counterpart, used for some operations.\n- @sugarfi for the initial Python Client for Crosis. (This has been tampered with and published to PyPI)\n- And everyone on the [Replit Discord Server](https://replit.com/discord) for the motivation, and general help.\n",
    'author': 'SnowCoder',
    'author_email': 'donot@email.me',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
