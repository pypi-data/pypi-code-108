# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['sunspecdemo']

package_data = \
{'': ['*']}

install_requires = \
['attrs==18.2.0',
 'click==7.1.2',
 'importlib-metadata>=4.10.1,<5.0.0',
 'importlib>=1.0.4,<2.0.0',
 'pysunspec==2.1.1',
 'setuptools==53.0.0',
 'toml>=0.10.2,<0.11.0',
 'toolz==0.9.0',
 'tqdm==4.32.1',
 'typing-extensions>=4.0.1,<5.0.0']

entry_points = \
{'console_scripts': ['sunspecdemo = sunspecdemo.cli:cli']}

setup_kwargs = {
    'name': 'sunspecdemo',
    'version': '0.1.5',
    'description': 'EPC SunSpec demonstration tool',
    'long_description': None,
    'author': 'Alex Anker',
    'author_email': 'alex.anker@epcpower.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
