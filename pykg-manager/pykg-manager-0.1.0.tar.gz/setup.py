# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['_tbnf',
 '_tbnf.FableSedlex',
 '_tbnf.fable_modules',
 '_tbnf.fable_modules.fable_library',
 'pykg']

package_data = \
{'': ['*']}

install_requires = \
['diskcache>=5.4.0,<6.0.0',
 'dulwich>=0.20.30,<0.21.0',
 'lark>=0.11.3,<0.12.0',
 'loguru>=0.5.3,<0.6.0',
 'tomli-w>=1.0.0,<2.0.0',
 'typing-extensions>=4.0.1,<5.0.0',
 'wisepy2>=1.2.1,<2.0.0',
 'z3-solver>=4.8.14,<5.0.0']

entry_points = \
{'console_scripts': ['pykg = pykg.cli_apis:main']}

setup_kwargs = {
    'name': 'pykg-manager',
    'version': '0.1.0',
    'description': 'A proposal Fable Python package manager',
    'long_description': None,
    'author': 'thautwarm',
    'author_email': 'twshere@outlook.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/thautwarm/reflect',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8.0,<4.0.0',
}


setup(**setup_kwargs)
