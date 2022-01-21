# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pathlib_tree', 'pathlib_tree.mounts', 'pathlib_tree.mounts.platform']

package_data = \
{'': ['*']}

install_requires = \
['cli-toolkit>=2.0,<3.0', 'filemagic>=1.6,<2.0']

extras_require = \
{':sys_platform == "win32"': ['python-magic-bin>=0.4.14,<0.5.0']}

setup_kwargs = {
    'name': 'pathlib-tree',
    'version': '2.1.3',
    'description': 'Filesystem tree utilities',
    'long_description': None,
    'author': 'Ilkka Tuohela',
    'author_email': 'hile@iki.fi',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
