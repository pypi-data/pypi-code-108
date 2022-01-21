# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pytoil',
 'pytoil.api',
 'pytoil.cli',
 'pytoil.config',
 'pytoil.environments',
 'pytoil.git',
 'pytoil.repo',
 'pytoil.starters',
 'pytoil.vscode']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML==6.0',
 'aiofiles==0.8.0',
 'anyio==3.5.0',
 'asyncclick==8.0.3.2',
 'attrs==21.4.0',
 'cookiecutter==1.7.3',
 'httpx-cache==0.4.0',
 'httpx[http2]==0.21.3',
 'humanize==3.13.1',
 'pydantic==1.9.0',
 'questionary==1.10.0',
 'rich==11.0.0',
 'thefuzz[speedup]==0.19.0',
 'tomlkit==0.8.0',
 'virtualenv==20.13.0',
 'wasabi==0.9.0']

entry_points = \
{'console_scripts': ['pytoil = pytoil.cli.root:main']}

setup_kwargs = {
    'name': 'pytoil',
    'version': '0.23.1',
    'description': 'CLI to automate the development workflow.',
    'long_description': "![logo](https://github.com/FollowTheProcess/pytoil/raw/main/docs/img/logo.png)\n\n[![License](https://img.shields.io/github/license/FollowTheProcess/pytoil)](https://github.com/FollowTheProcess/pytoil)\n[![PyPI](https://img.shields.io/pypi/v/pytoil.svg?logo=python)](https://pypi.python.org/pypi/pytoil)\n[![GitHub](https://img.shields.io/github/v/release/FollowTheProcess/pytoil?logo=github&sort=semver)](https://github.com/FollowTheProcess/pytoil)\n[![Code Style](https://img.shields.io/badge/code%20style-black-black)](https://github.com/FollowTheProcess/pytoil)\n[![CI](https://github.com/FollowTheProcess/pytoil/workflows/CI/badge.svg)](https://github.com/FollowTheProcess/pytoil/actions?query=workflow%3ACI)\n[![Coverage](https://github.com/FollowTheProcess/pytoil/raw/main/docs/img/coverage.svg)](https://github.com/FollowTheProcess/pytoil)\n\n*pytoil is a small, helpful CLI to help developers manage their local and remote projects with ease!*\n\n* **Source Code**: [https://github.com/FollowTheProcess/pytoil](https://github.com/FollowTheProcess/pytoil)\n\n* **Documentation**: [https://FollowTheProcess.github.io/pytoil/](https://FollowTheProcess.github.io/pytoil/)\n\n## What is it?\n\n`pytoil` is a handy tool that helps you stay on top of all your projects, remote or local. It's primarily aimed at python developers but you could easily use it to manage any project!\n\npytoil is:\n\n* Easy to use ✅\n* Easy to configure ✅\n* Safe (it won't edit your repos at all) ✅\n* Snappy (it's asynchronous from the ground up and as much as possible is done concurrently, clone all your repos in seconds!) 💨\n* Useful! (I hope 😃)\n\nSay goodbye to janky bash scripts 👋🏻\n\n## Background\n\nLike many developers I suspect, I quickly became bored of typing repeated commands to manage my projects, create virtual environments, install packages, fire off `cURL` snippets to check if I had a certain repo etc.\n\nSo I wrote some shell functions to do some of this for me...\n\nAnd these shell functions grew and grew and grew.\n\nUntil one day I saw that the file I kept these functions in was over 1000 lines of bash (a lot of `printf`'s so it wasn't all logic but still). And 1000 lines of bash is *waaaay* too much!\n\nAnd because I'd basically hacked it all together, it was **very** fragile. If a part of a function failed, it would just carry on and wreak havoc! I'd have to do `rm -rf all_my_projects`... I mean careful forensic investigation to fix it.\n\nSo I decided to make a robust CLI with the proper error handling and testability of python, and here it is! 🎉\n\n## Installation\n\nAs pytoil is a CLI program, I'd recommend installing with [pipx].\n\n```shell\n$ pipx install pytoil\n---> 100%\nSuccessfully installed pytoil\n```\n\nYou can always fall back to pip\n\n```shell\n$ python3 -m pip install pytoil\n---> 100%\nSuccessfully installed pytoil\n```\n\npytoil will install everything it needs *in python* to work. However, it's full feature set can only be accessed if you have the following external dependencies:\n\n* [git]\n* [conda] (if you work with conda environments)\n* [VSCode] (if you want to use pytoil to automatically open your projects for you)\n* [poetry] (if you want to create poetry environments)\n* [flit] (if you want to create flit environments)\n\n## Quickstart\n\n`pytoil` is super easy to get started with.\n\nAfter you install pytoil, the first time you run it you'll get something like this.\n\n```plain\n$ pytoil <any command>\n\nNo pytoil config file detected!\n? Interactively configure pytoil? [y/n]\n```\n\nIf you say yes, pytoil will walk you through a few questions and fill out your config file with the values you enter. If you'd rather not do this interactively, just say no and it will instead put a default config file in the right place for you to edit later.\n\nOnce you've configured it properly, you can do things like...\n\n#### See your local and remote projects\n\n```plain\n$ pytoil show local\nLocal Projects\n\nShowing 3 out of 3 local projects\n\n  Name              Created          Modified\n ───────────────────────────────────────────────────\n  project 1         13 days ago      9 days ago\n  project 2         a day ago        a minute ago\n  project 3         a month ago      a month ago\n```\n\n#### See which ones you have on GitHub, but not on your computer\n\n```plain\n$ pytoil show diff\nDiff: Remote - Local\n\nShowing 3 out of 3 projects\n\n  Name             Size       Created                Modified\n ─────────────────────────────────────────────────────────────────────────\n  remote 1         154.6 kB   a month ago            29 days ago\n  remote 2         2.1 MB     1 year, 15 days ago    11 months ago\n  remote 3         753.7 kB   1 year, 6 months ago   a month ago\n```\n\n#### Easily grab a project, regardless of where it is\n\n```plain\n$ pytoil checkout myproject\n\n// Will now either open that project if local\n// or clone it, then open it if not\n```\n\n#### Create a new project and virtual environment in one go\n\n```plain\n$ pytoil new myproject --venv venv\n\nCreating project: 'myproject' at '/Users/you/projects/myproject'\n\nCreating virtual environment for: 'myproject'\n```\n\n#### And even do this from a [cookiecutter] template\n\n```plain\n$ pytoil new myproject --venv venv --cookie https://github.com/some/cookie.git\n\nCreating project: 'myproject' with cookiecutter template: 'https://github.com/some/cookie.git'\n\n// You'll then be asked all the cookiecutter questions defined in the template\n// After which pytoil will take over and create the virtual environment as normal\n```\n\nAnd loads more!\n\n### Help\n\nLike all good CLI programs, pytoil (as well as all it's subcommands, and all *their* subcommands!) has a `--help` option to show you what to do.\n\n```plain\n$ pytoil --help\n\nUsage: pytoil [OPTIONS] COMMAND [ARGS]...\n\n  Helpful CLI to automate the development workflow.\n\n  - Create and manage your local and remote projects\n\n  - Build projects from cookiecutter templates.\n\n  - Easily create/manage virtual environments.\n\n  - Minimal configuration required.\n\nOptions:\n  --version  Show the version and exit.\n  --help     Show this message and exit.\n\nCommands:\n  checkout  Checkout an existing development project.\n  config    Interact with pytoil's configuration.\n  docs      Open pytoil's documentation in your browser.\n  find      Quickly locate a project.\n  gh        Open one of your projects on GitHub.\n  info      Get useful info for a project.\n  new       Create a new development project.\n  pull      Pull down your remote projects.\n  remove    Remove projects from your local filesystem.\n  show      View your local/remote projects.\n```\n\npytoil's CLI is designed such that if you don't specify any arguments, it won't do anything! just show you the `--help`. This is called being a 'well behaved' unix command line tool.\n\nThis is true for any subcommand of pytoil so you won't accidentally break anything if you don't specify arguments 🎉\n\nAnd if you get truly stuck, you can quickly open pytoil's documentation with:\n\n```plain\n$ pytoil docs\n\nOpening pytoil's documentation in your browser...\n\n# Now you'll be on this page in whatever your default browser is!\n```\n\nCheck out the [docs] for more 💥\n\n## Contributing\n\n`pytoil` is an open source project and, as such, welcomes contributions of all kinds 😃\n\nYour best bet is to check out the [contributing guide] in the docs!\n\n[pipx]: https://pipxproject.github.io/pipx/\n[docs]: https://FollowTheProcess.github.io/pytoil/\n[FollowTheProcess/poetry_pypackage]: https://github.com/FollowTheProcess/poetry_pypackage\n[wasabi]: https://github.com/ines/wasabi\n[httpx]: https://www.python-httpx.org\n[async-click]: https://github.com/python-trio/asyncclick\n[contributing guide]: https://followtheprocess.github.io/pytoil/contributing/contributing.html\n[git]: https://git-scm.com\n[conda]: https://docs.conda.io/en/latest/\n[VSCode]: https://code.visualstudio.com\n[config]: config.md\n[cookiecutter]: https://github.com/cookiecutter/cookiecutter\n[poetry]: https://python-poetry.org\n[flit]: https://flit.readthedocs.io\n",
    'author': 'Tom Fleet',
    'author_email': 'tomfleet2018@gmail.com',
    'maintainer': 'Tom Fleet',
    'maintainer_email': 'tomfleet2018@gmail.com',
    'url': 'https://github.com/FollowTheProcess/pytoil',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
