# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cpenv',
 'cpenv.cli',
 'cpenv.repos',
 'cpenv.vendor',
 'cpenv.vendor.cachetools',
 'cpenv.vendor.certifi',
 'cpenv.vendor.shotgun_api3',
 'cpenv.vendor.shotgun_api3.lib',
 'cpenv.vendor.shotgun_api3.lib.certifi',
 'cpenv.vendor.shotgun_api3.lib.httplib2',
 'cpenv.vendor.shotgun_api3.lib.httplib2.python2',
 'cpenv.vendor.shotgun_api3.lib.httplib2.python3',
 'cpenv.vendor.shotgun_api3.lib.mockgun',
 'cpenv.vendor.yaml',
 'cpenv.vendor.yaml.yaml2',
 'cpenv.vendor.yaml.yaml3']

package_data = \
{'': ['*'], 'cpenv': ['bin/*']}

install_requires = \
['colorama>=0.4.3,<0.5.0', 'psutil>=5.7.0,<6.0.0', 'tqdm>=4.46.0,<5.0.0']

entry_points = \
{'console_scripts': ['cpenv = cpenv.__main__:main']}

setup_kwargs = {
    'name': 'cpenv',
    'version': '0.5.28',
    'description': 'Cross-platform module and environment management.',
    'long_description': '<p align="center">\n    <img src="https://raw.github.com/cpenv/cpenv/master/res/icon_dark.png"/>\n</p>\n\n# cpenv\nManage software plugins, project dependencies and environment\nvariables using Modules.\n\n<p align="center">\n    <img src="https://raw.github.com/cpenv/cpenv/master/res/demo.gif"/>\n</p>\n\n# Installation\nThe recommended method of installing cpenv is via [pipx](https://pipxproject.github.io/pipx).\nPipx is used to install python cli applications in isolation.\n\n```\npipx install cpenv\n```\n```\npipx upgrade cpenv\n```\n```\npipx uninstall cpenv\n```\n\n# Overview\nCpenv is a cli tool and python library used to create, edit, publish, and activate Modules. A Module is a folder containing a dependency, like Arnold for Maya, and a module file that configures it.\n\n## Environment Variables\n| Variable                 | Description                            | Default |\n| ------------------------ | -------------------------------------- | ------- |\n| CPENV_HOME               | Customize path to cpenv home           |         |\n| CPENV_DISABLE_PROMPT     | Disable prompt when modules activated  | 0       |\n| CPENV_ACTIVE_MODULES     | List of activated modules              |         |\n| CPENV_SHELL              | Preferred subshell like "powershell"   |         |\n\n## Example Modules\n- [snack](https://github.com/cpenv/snack)\n\n## Create a Module\nUse `cpenv create <module>` to use a guide to create a new Module.\nThis will create a new folder in your current working directory with a module file in it.\n\n## Edit a Module\nEach Module contains a module.yml file, referred to as a module file. A module file contains metadata like the name and version of a module, as well as configuration, like environment variables.\n```\n# Variables\n# $MODULE - path to this module\n# $PLATFORM - platform name (win, mac, linux)\n# $PYVER - python version (2.7, 3.6...)\n\n# Wrap variables in brackets when they are nested within a string.\n#     DO \'this${variable}isnested/\' NOT \'this$variableisnested\'\n\nname: \'my_module\'\nversion: \'0.1.0\'\ndescription: \'My first module.\'\nauthor: \'Me\'\nemail: \'me@email.com\'\nrequires: []\nenvironment:\n    MY_MODULE_VAR: \'Test\'\n```\n\n### Environment key\nSetting a value will insert a key or overwrite it\'s existing value.\n```\nSOME_VAR: \'SOME_VALUE\'\n```\n\nUse the $MODULE variable for module relative paths.\n```\nRELATIVE_VAR: $MODULE/bin\n```\n\nUse lists to prepend values to a key.\n```\nPATH:\n    - $MODULE/bin\n```\n\nUse `win`, `linux` and `mac or osx` keys to declare platform specific values. If you leave out a platform, the variable will not be included on that platform.\n```\nPLATFORM_VAR:\n    mac: /mnt/some/path\n    linux: /Volumes/some/path\n    win: C:/some/path\n```\n\nYou can also use platform keys when prepending values to a variable.\n```\nPATH:\n    - mac: $MODULE/macattack\n      linux: $MODULE/penguin\n      win: $MODULE/squares\n```\n\nReuse environment variables to simplify things.\n```\nBASE: $MODULE/$PLATFORM/base\nPATH:\n    - $BASE/bin\nPYTHONPATH:\n    - $BASE/python\n```\n\n#### Advanced\nThe implicit set and prepend operations above cover the most common use cases when modifying environment variables. For more advanced use cases you can use the following explicit operation keys.\n```\nSVAR:\n    set:\n        - Value0\n        - Value1\nPVAR:\n    prepend:\n        - X\nRVAR:\n    unset: 1\nPATH:\n    remove:\n        - C:/Python27\n        - C:/Python27/Scripts\nPYTHONPATH:\n    append:\n        - $MODULE/python\n        - $MODULE/lib\n```\n\nYou can also uses lists of opreations to perform complex modifications.\n```\nPATH:\n    - remove: /some/file/path\n    - append: /some/other/path\n    - prepend: /one/more/path\n```\n\nOne workflow that this enables is the use of modules solely for the purpose of overriding environment variables. Imagine you have a module `my_tool` and it uses a variable `MY_TOOL_PLUGINS` to lookup plugins.\n```\nname: my_tool\n...\nenvironment:\n    MY_TOOL_PLUGINS:\n        - //studio/dev/my_tool/plugins\n        - //studio/projects/test_project/plugins\n```\n\nNow imagine you have a new project and you want `my_tool` to look at a different location for plugins just for that project. Rather than create a new version of the `my_tool` module, create a override module. We might name this module after our project, `project_b`.\n```\nname: project_b\n...\nenvironment:\n    MY_TOOL_PLUGINS:\n        set:\n            - //studio/prod/my_tool/plugins\n            - //studio/projects/project_b/plugins\n```\n\nAll we have to do is activate `my_tool` and `project_b` in that order to make sure our overrides are used.\n```\n> cpenv activate my_tool project_b\n```\n\n#### Requires key\nThe requires key is a list of dependencies that a module needs to function. Currently this is only used for reference, these modules will not be activated automatically.\n\n## Test a Module\nWhen you\'re working on a module navigate into it\'s root directory. Then you can activate it using `cpenv activate .`. This is\nthe best way to validate your module prior to publishing.\n\n## Publish a Module\nOnce you\'re Module is ready for production, use `cpenv publish .` to publish it. Publishing a Module uploads it to a Repo of your choosing.\n\n# Repos\nRepos are storage locations for Modules that support finding, listing, uploading, and downloading Modules via *requirements* like\n`my_module-0.1.0`. Cpenv is configured with the following LocalRepos by default:\n\n- **cwd** - Your current working directory\n- **user** - A user specific repo\n- **home** - A machine wide repo\n\nUse `cpenv repo list` to display your configured Repos. LocalRepos point directly to folders on your local file system.\nCustomize the home Repo by setting the `CPENV_HOME` environment variable.\n\nWhen you activate a module using a requirement, all configured Repos are searched and the best match is used. If the resolved\nmodule is not in a LocalRepo it will be downloaded to your home Repo then activated. This is one of the key features of cpenv\nand allows for strong distributed workflows. For example, you can configure a remote repo like the ShotgunRepo and store your modules directly in a\n[Shotgun studio](https://www.shotgunsoftware.com/) database. [Visit the tk-cpenv repository for more info on using cpenv with Shotgun](https://github.com/cpenv/tk-cpenv)\n\n# Requirements\nRequirements are strings used to resolve and activate modules in Repos. They can be versionless like `my_module` or require a\nversion like `my_module-0.1.0`. Cpenv supports semver/calver, simple versions (v1), and what I like to call *weird* versions\nlike 12.0v2 (The Foundry products). In the future cpenv may support more complex requirements by utilizing\n[resolvelib](https://github.com/sarugaku/resolvelib).\n',
    'author': 'Dan Bradham',
    'author_email': 'danielbradham@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
