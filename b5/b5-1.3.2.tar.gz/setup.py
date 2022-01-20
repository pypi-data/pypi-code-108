# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['b5', 'b5.lib', 'b5.modules', 'b5.tests.lib']

package_data = \
{'': ['*'], 'b5': ['bash/*', 'legacy/*', 'legacy/modules/*']}

install_requires = \
['Jinja2>=3.0.1,<4.0.0',
 'MarkupSafe>=2.0.1,<3.0.0',
 'PyYAML>=6.0,<7.0',
 'packaging>=21.3,<22.0',
 'termcolor>=1.1.0,<2.0.0']

entry_points = \
{'console_scripts': ['b5 = b5.main:main',
                     'b5-execute = b5.execute:main',
                     'b5-init = b5.init:main']}

setup_kwargs = {
    'name': 'b5',
    'version': '1.3.2',
    'description': 'b5 - simple and sane task runner',
    'long_description': '![b5 ready](assets/badges/b5_ready.png)\n\n# b5 Task Runner\n\nb5 is the central task runner for all projects of our agency (TEAM23 - www.team23.de). It tries to be as simple\nas possible while empowering you to write your own tasks, extend existing ones and use b5 for all of the everyday\nproject jobs.\n\n## Basic usage and concept\n\n`b5 {taskname}` will look for a file called [`Taskfile`](docs/02_Taskfile_format.md) found under build/ in your project\nroot. It will then execute the function named `task:{taskname}` inside the Taskfile (which is a normal bash script).\nThis means you may call `b5 install` to have the function `task:install` run.\n\nThe basic idea of b5 is to allow you to easily put your daily shell jobs into the Taskfile and provide a\ncommon schema for running these tasks. So `b5 css` for example will always build the CSS files for your\nproject regardless of the CSS preprocessor used in this particular project (could be: less, sass, …). As b5\nuses bash scripting as the Taskfile format it is easy to understand and enhance.\n\nb5 in addition provides some modules to ease the usage of some common tools used in web development (like\n[npm](docs/modules/npm.md), [composer](docs/modules/composer.md), [pipenv](docs/modules/pipenv.md),\n[docker](docs/modules/docker.md), …). In addition it defines some\n[common task names](docs/03_common_tasks.md) to introduce a good convention for your task naming schema. This\nwill allow new developers to get on board faster - not need to care too much about the\nproject setup itself.\n\nYou may pass parameters to your tasks like `b5 some_task some_parameter` and use normal bash parameter handling\nto use these parameters (`$1`, or better `${1}`). Please note that b5 will abort when accessing a non existent\nparameter, use bash default values when necessary (`${1:-default}`).\n\n**Hint:** You may add a file called Taskfile.local (`build/Taskfile.local`) for all your personal tasks. Make\nsure to never add this file to git. Please be sure to add this file to your .gitignore. Otherwise you might\ninterfere with the local Taskfile of your colleges.\n\n## Quick start\n\nInstall b5 using `pipsi install b5` or `pip install b5` (For Mac OS X you may use `brew install b5` after\nadding our tap). See [detailed installation instructions](docs/00_install.md).\n\n**Note for my TEAM23 colleagues:** Please make sure to install the\n[additional dependencies](docs/00_install.md#additional-dependencies).\n\n### Starting your project\n\n```bash\nb5-init example-project\ncd example-project\n# start working on the new project\n```\n\n**Note:** You may use `b5-init -s $SKELETON example` to initialize the project using an skeleton. By default\nb5 will use the "basic" skeleton. See [project initialization](docs/06_project_init.md) for more details.\n\n### Defining your tasks (build/Taskfile)\n\nb5 initialized your project with an example Taskfile (see `build/Taskfile`). For adding new tasks just\nwrite bash functions prefixed with `task:`, like:\n\n```bash\n#!/usr/bin/env bash\n# b5 Taskfile, see https://git.team23.de/build/b5 for details\n\ntask:make_it_happen() {\n    echo "Yeah, it happened"\n}\n```\n\n### Running your tasks\n\nNow you can use `b5 make_it_happen` and your code inside the function will run. As this code is a simple\nbash script you may use your normal command line tools. Feel free to use gulp, grunt, fabric, … for more\ncomplex task excution - and call these using your Taskfile.\n\n**Note:** The Taskfile is always executed inside the "run-path", which defaults to `build/`. Make\nsure to switch path, when neccessary. I recommend using a subshell (see\n["( … )" subshell syntax](http://www.gnu.org/software/bash/manual/html_node/Command-Grouping.html)) when\ndoing so.\n\n## Going further\n\nNow you set up a simple example project including an example Taskfile. The Taskfile is the central part of\nthe b5 task runner which will include the calls to all of the provided tasks. Most of the tasks will\ncall external tools like, gulp or fabric. This is the intended behavior.\n\nSee [detailed installation instruction](docs/00_install.md) for some more details the installation of b5.\n\nSee [core concepts](docs/01_concepts.md) for some more details about the b5 concepts.\n\nSee [Taskfile format](docs/02_Taskfile_format.md) for more details on how to write your Taskfile.\n\nSee [common tasks](docs/03_common_tasks.md) for information about which tasks your Taskfile needs\nto provide and what these tasks should do.\n\nSee [Configuration](docs/04_config.md) for about how to add configuration to the build process and how\nto handle local configuration.\n\nSee [modules](docs/05_modules.md) for looking further into modules b5 already provides for a healthy\nproject setup.\n\nSee [project initialization](docs/06_project_init.md) for more information about how to `b5-init` a project.\n\n## b5 logo\n\nYou may use the b5 logo when referring to b5:  \n![b5 Logo](assets/logo_small.png)  \n(see [assets/](assets/) for other formats)\n\nAlso feel free to add a b5 badge to your project after you made it "b5 ready":  \n![b5 ready](assets/badges/b5_ready.png)  \n(see [assets/badges/](assets/badges/) for other formats)\n',
    'author': 'David Danier',
    'author_email': 'danier@team23.de',
    'maintainer': 'David Danier',
    'maintainer_email': 'danier@team23.de',
    'url': 'https://github.com/team23/b5',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
