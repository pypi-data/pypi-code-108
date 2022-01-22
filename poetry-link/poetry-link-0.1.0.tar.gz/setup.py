# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['poetry_link']

package_data = \
{'': ['*']}

install_requires = \
['flit-core>=3.2,<4.0', 'flit>=3.6.0,<4.0.0', 'poetry>=1.2.0a2,<2.0.0']

entry_points = \
{'poetry.application.plugin': ['link-command = '
                               'poetry_link._plugin:PoetryLinkPlugin']}

setup_kwargs = {
    'name': 'poetry-link',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Niklas Rosenstein',
    'author_email': 'rosensteinniklas@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
