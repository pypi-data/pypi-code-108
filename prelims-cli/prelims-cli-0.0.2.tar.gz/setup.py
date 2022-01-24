# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['prelims_cli', 'prelims_cli.config', 'prelims_cli.ja']

package_data = \
{'': ['*']}

install_requires = \
['hydra-core>=1.1.1,<2.0.0',
 'numpy>=1.22.1,<2.0.0',
 'prelims>=0.0.5,<0.0.6',
 'scipy>=1.7.3,<2.0.0',
 'taskipy>=1.9.0,<2.0.0']

extras_require = \
{'ja': ['SudachiPy>=0.6.2,<0.7.0', 'SudachiDict-full>=20211220,<20211221']}

entry_points = \
{'console_scripts': ['prelims-cli = prelims_cli.cli:main']}

setup_kwargs = {
    'name': 'prelims-cli',
    'version': '0.0.2',
    'description': 'prelims CLI - Front matter post-processor CLI',
    'long_description': None,
    'author': 'Aki Ariga',
    'author_email': 'chezou@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<3.11',
}


setup(**setup_kwargs)
