# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['poetry_multiproject_plugin',
 'poetry_multiproject_plugin.commands',
 'poetry_multiproject_plugin.overrides',
 'poetry_multiproject_plugin.repo']

package_data = \
{'': ['*']}

install_requires = \
['poetry>=1.2.0a2,<2.0.0']

entry_points = \
{'poetry.application.plugin': ['poetry-multiproject-plugin = '
                               'poetry_multiproject_plugin:MultiProjectPlugin']}

setup_kwargs = {
    'name': 'poetry-multiproject-plugin',
    'version': '0.2.0',
    'description': 'A Poetry plugin that aims to simplify package & dependency management for projects in Monorepos.',
    'long_description': '# Poetry Multiproject Plugin\n\nThis is a Python `Poetry` plugin, adding commands with support for including packages outside of a project root.\n\nThis is achieved by setting the workspace (or commonly the repo) folder as the root folder.\nAlso, the plugin makes it possible specify a project specific TOML file.\n\nExample usage:\nrunning the command from the workspace root folder\n\n``` shell\npoetry build-project --t path/to/myproject.toml\n```\n\nOptionally, run the command from the same folder as the actual project specific TOML file:\n\n``` shell\npoetry build-project\n```\n\n## Why?\nBeing able to specify package includes outside of a project root is especially\nuseful when structuring code in a Monorepo, where projects can share components.\n\nWhen the plugin is installed, there is a new command available: `build-project`.\n\n## How is it different from the "poetry build" command?\nPoetry doesn\'t seem allow to reference code that is outside of the __project__ root.\n\nSomething like this will cause the build to fail:\n\n``` shell\n# this will fail using the default poetry build command\n\npackages = [\n    { include = "the_code_in_my_project"\n    { include = "../../../my-shared-package" }]\n```\n\nBy explicitly setting a workspace root, it is possible to reference outside components like this:\n\n``` shell\npackages = [\n    { include = "my/project/path/the_code_in_my_project"\n    { include = "shared/a-shared-package" }]\n```\n\nThe project specific code is referenced with a path starting from the workspace root. The external includes can now be\nreferenced as if the project specific TOML were located at the root.\n\n\n``` shell\nprojects/\n  my-app/\n    pyproject.toml (including a shared package)\n    app.py\n\n  my-service/\n    pyproject.toml (including other shared packages)\n    app.py\n\nshared/\n  my-package/\n   __init__.py\n   code.py\n\n  my-other-package/\n   __init__.py\n   code.py\n\n.workspace (a file that tells the plugin where to find the workspace root)\n```\n\nAs a fallback, the plugin will look for a `pyproject.toml` or a `.git` folder to determine the workspace root.\n\n\n## Using the preview of Poetry\nThis plugin depends on a preview of [Poetry](https://python-poetry.org/) with functionality for adding custom Plugins.\nHave a look at the [official Poetry preview docs](https://python-poetry.org/docs/master/) for how to install it.\n\nInstall the plugin according to the [official Poetry docs](https://python-poetry.org/docs/master/cli/#plugin).\n\nWhen installed, there will be a new command available: `build-project`.\n\n\n## Modifying the Poetry internals\nSetting the workspace root is done by altering the internal properties of the Poetry objects.\nThis is (naturally) a risk, an update of the Poetry tool could break the functionality of the plugin.\n\nA long-term goal is to make a Pull Request to the Poetry repository, making this kind of functionality available\nin there. If (when?) that is done, this plugin would no longer be necessary.\n\n## What\'s next? Any other commands?\nStarting with the `build-project` command, and planning to add more custom commands that are\nrelevant when using a project specific TOML file.\n\nMaybe continue with a `install-project` command?\n',
    'author': 'David Vujic',
    'author_email': 'None',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/davidvujic/poetry-multiproject-plugin',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
