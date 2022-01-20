# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['plaster_yaml']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0', 'plaster>=1.0,<2.0']

setup_kwargs = {
    'name': 'plaster-yaml',
    'version': '0.1.3',
    'description': 'A plaster plugin to configure pyramid app with Yaml',
    'long_description': '# Plaster Yaml\n\n## Introduction\n\nBy default, Pyramid use a paste format file to loads its configuration,\n\nhere is a plugin to use a yaml file instead to configure your pyramid\napplication.\n\ne.g.\n\n```\npserve development.yaml\n```\n\n## Installation\n\n## With poetry\n\n```\npoetry add plaster-yaml\n```\n\n## With pip\n\n```\npip install plaster-yaml\n```\n\n## Usage\n\n## With poetry\n\nYou need to register this plugin in your `pyproject.toml`:\n\n\n```\n[tool.poetry.plugins."paste.app_factory"]\nmain = "<PATH_TO_MODULE_CONTAINING_MAIN>:main"\n\n[tool.poetry.plugins."plaster.loader_factory"]\n"file+yaml" = "plaster_yaml:Loader"\n```\n\nYou must run `poetry install` to finalize the registration.\n\n## With setuptools\n\n```\nsetup(\n    ...,\n    entry_points={\n     \'paste.app_factory\': [\'main = <my_app>:main\'],\n     \'plaster.loader_factory\': [\'yaml = plaster_yaml:Loader\'],\n     ...\n    },\n)\n```\n\nYou must run `pip install -e .` to finallize the registration.\n\n## Troubleshouting\n\nIf you get the following exception:\n\n```\nplaster.exceptions.LoaderNotFound: Could not find a matching loader for the scheme "file+yaml", protocol "wsgi".\n```\n\nIt meast that you did not register the pluging. Read the usage section\nfor to register it properly.\n\n',
    'author': 'Guillaume Gauvrit',
    'author_email': 'guillaume@gauvr.it',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
