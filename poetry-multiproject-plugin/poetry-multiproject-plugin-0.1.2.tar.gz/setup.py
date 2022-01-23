# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['poetry_multiproject_plugin']

package_data = \
{'': ['*']}

install_requires = \
['poetry>=1.2.0a2,<2.0.0']

entry_points = \
{'poetry.application.plugin': ['poetry-multiproject-plugin = '
                               'poetry_multiproject_plugin:MultiProjectPlugin']}

setup_kwargs = {
    'name': 'poetry-multiproject-plugin',
    'version': '0.1.2',
    'description': 'A Poetry plugin that makes it possible to build projects with custom TOML files.',
    'long_description': '# Poetry Multiproject Plugin\n\nThis is a `Poetry` plugin that will make it possible to build projects using custom TOML files.\n\nThis is especially useful when structuring code in a Monorepo, containing several projects.\n\nWhen installed, there will be a new command available: `build-project`.\n\n## How is it different from the "poetry build" command?\nAs I understand it, Poetry doesn\'t allow to reference code that is outside of the __project__ root.\n\nSomething like:\n\n``` shell\npackages = [{ include = "../../../my-package" }]\n\n```\n\nAs an alternative to have a `pyproject.toml` file in a subfolder, this plugin supports a Monorepo file structure like this:\n\n```\nmy-app/\n   app.py\n\nmy-service/\n   app.py\n\nmy-package/\n   __init__.py\n   my_package.py\n\nmy-other-package/\n   __init__.py\n   my_other_package.py\n\npyproject.toml\nmy-app.toml\nmy-service.toml\n...\n```\n\nThe different `TOML` files can include different local dependencies.\nLet\'s say that `my-app` imports `my-package`, and `my-service` imports `my-package` only.\n\n`my-app` and `my-service` can be built separately and include the local packages needed. By being placed at the __workspace__ root, will not cause\nany issues with relative paths.\n\n\n## Usage\nThis plugin depends on a preview of [Poetry](https://python-poetry.org/) with functionality for adding custom Plugins.\nHave a look at the [official Poetry preview docs](https://python-poetry.org/docs/master/) for how to install it.\n\nInstall the plugin according to the [official Poetry docs](https://python-poetry.org/docs/master/cli/#plugin).\n\nWhen installed, there will be a new command available: `build-project`.\n\nThis command will build your project, just like the `poetry build` command, but with a custom project TOML file.\n\n``` shell\npoetry build-project --t myproject.toml\n```\n\n(use `--t` or `--toml` to specify your custom TOML file to use)\n\n',
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
