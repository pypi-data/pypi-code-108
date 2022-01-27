# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['aprofiles',
 'aprofiles.detection',
 'aprofiles.io',
 'aprofiles.plot',
 'aprofiles.retrieval',
 'aprofiles.simulation']

package_data = \
{'': ['*'], 'aprofiles': ['config/*']}

install_requires = \
['matplotlib>=3.5.0,<4.0.0',
 'miepython>=2.2.1,<3.0.0',
 'netCDF4>=1.5.8,<2.0.0',
 'numpy>=1.21.4,<2.0.0',
 'scipy>=1.7.2,<2.0.0',
 'seaborn>=0.11.2,<0.12.0',
 'tqdm>=4.62.3,<5.0.0',
 'typer>=0.4.0,<0.5.0',
 'xarray>=0.20.1,<0.21.0']

extras_require = \
{'docs': ['sphinx>=4.3.0,<5.0.0',
          'pydata-sphinx-theme>=0.7.2,<0.8.0',
          'recommonmark>=0.7.1,<0.8.0']}

setup_kwargs = {
    'name': 'aprofiles',
    'version': '0.4.0',
    'description': 'Analysis of atmospheric profilers measurements',
    'long_description': None,
    'author': 'augustinm',
    'author_email': 'augustinm@met.no',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.8,<3.10',
}


setup(**setup_kwargs)
