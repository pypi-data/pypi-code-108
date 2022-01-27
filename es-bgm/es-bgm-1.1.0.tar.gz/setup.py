# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['bgm']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0',
 'confuse>=1.7.0,<2.0.0',
 'deepmerge>=1.0.1,<2.0.0',
 'psutil>=5.9.0,<6.0.0',
 'pydantic>=1.9.0,<2.0.0',
 'pygame>=2.0.1,<3.0.0',
 'python-decouple>=3.4,<4.0',
 'transitions>=0.8.10,<0.9.0']

extras_require = \
{'lint': ['pylint']}

entry_points = \
{'console_scripts': ['esbgm = bgm:main']}

setup_kwargs = {
    'name': 'es-bgm',
    'version': '1.1.0',
    'description': 'Allows you to add background music to EmulationStation',
    'long_description': None,
    'author': 'David',
    'author_email': 'davigetto@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
