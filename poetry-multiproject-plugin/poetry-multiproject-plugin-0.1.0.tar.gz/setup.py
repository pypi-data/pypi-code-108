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
    'version': '0.1.0',
    'description': 'A Poetry plugin that makes it possible to build projects with custom TOML files.',
    'long_description': '# Poetry Multiproject Plugin\n\nThis is a `Poetry` plugin that will make it possible to build projects using custom TOML files.\n\nThis is especially useful when structuring code in a Monorepo, containing several projects.\n\nNote: the current version (`0.1.0`) depends on a preview of [Poetry](https://python-poetry.org/) with functionality for adding custom Plugins.\nHave a look at the [official Poetry preview docs](https://python-poetry.org/docs/master/) for how to install it.\n\n\n## Usage\nInstall the plugin according to the [official Poetry docs](https://python-poetry.org/docs/master/cli/#plugin).\n\nWhen installed, there will be a new command available: `build-project`.\n\nThis command will build your project, just like the `poetry build` command, but with a custom project TOML file.\n\n``` shell\npoetry build-project --t myproject.toml\n```\n\n(use `--t` or `--toml` to specify your custom TOML file to use)\n\n',
    'author': 'David Vujic',
    'author_email': 'david@vujic.se',
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
