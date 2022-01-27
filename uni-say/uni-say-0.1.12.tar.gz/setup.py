# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['uni_say']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.0.3,<9.0.0']

entry_points = \
{'console_scripts': ['uni-say = uni_say.cli:cli']}

setup_kwargs = {
    'name': 'uni-say',
    'version': '0.1.12',
    'description': '',
    'long_description': '# uni-say\n\nSay something\n',
    'author': 'Eyal Levin',
    'author_email': 'eyalev@gmail.com',
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
