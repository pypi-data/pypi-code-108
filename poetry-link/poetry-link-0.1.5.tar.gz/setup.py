# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['poetry_link']

package_data = \
{'': ['*']}

install_requires = \
['flit>=3.6.0,<4.0.0', 'nr.util>=0.4.3,<0.5.0', 'poetry>=1.2.0a2,<2.0.0']

entry_points = \
{'poetry.application.plugin': ['link-command = '
                               'poetry_link._poetry_plugin:LinkPlugin']}

setup_kwargs = {
    'name': 'poetry-link',
    'version': '0.1.5',
    'description': 'Editable installs for packages developed with Poetry using Flit.',
    'long_description': "# poetry-lock\n\nPoetry natively does not support editable installs (as of writing this on Jan 22, 2022). This\ncommand makes use of the Flit backend to leverage its excellent symlink support. Relevant parts of\nthe Poetry configuration will by adpated such that no Flit related configuration needs to be added\nto pyproject.toml.\n\n## Example usage:\n\n    $ poetry link\n    Discovered modules in /projects/poetry-link/src: my_package\n    Extras to install for deps 'all': {'.none'}\n    Symlinking src/my_package -> .venv/lib/python3.10/site-packages/my_package\n\n## How it works\n\nFirst, the Poetry configuration in pyproject.toml will be updated temporarily to contain the\nrelevant parts in the format that Flit understands. The changes to the configuration include\n\n* copy tool.poetry.plugins -> tool.flit.entrypoints\n* copy tool.poetry.scripts -> tool.flit.scripts\n* add tool.flit.metadata\n  * the module is derived automatically using setuptools.find_namespace_packages() on the\n    src/ directory, if it exists, or otherwise on the current directory. Note that Flit\n    only supports installing one package at a time, so it will be an error if setuptools\n    discovers more than one package.\n\nThen, while the configuration is in an updated state, $ flit install -s --python python is\ninvoked. This will symlink your package into your currently active Python environment. (Note that right\nnow, the plugin does not support auto-detecting the virtual environment automatically created for you by\nPoetry and the environment in which you want to symlink the package to needs to be active).\n\nFinally, the configuration is reverted to its original state.\n",
    'author': 'Niklas Rosenstein',
    'author_email': 'rosensteinniklas@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
