# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['hmm_stock_forecast',
 'hmm_stock_forecast.data',
 'hmm_stock_forecast.error',
 'hmm_stock_forecast.hmm',
 'hmm_stock_forecast.plot',
 'hmm_stock_forecast.utils']

package_data = \
{'': ['*']}

install_requires = \
['argparse>=1.4.0,<2.0.0',
 'matplotlib>=3.5.1,<4.0.0',
 'numpy>=1.22.1,<2.0.0',
 'pandas-datareader>=0.10.0,<0.11.0',
 'pandas>=1.3.5,<2.0.0',
 'pomegranate>=0.14.7,<0.15.0',
 'recordclass>=0.17.1,<0.18.0',
 'sklearn>=0.0,<0.1',
 'tqdm>=4.62.3,<5.0.0']

entry_points = \
{'console_scripts': ['start = hmm_stock_forecast.main:main']}

setup_kwargs = {
    'name': 'hmm-stock-forecast',
    'version': '1.0',
    'description': 'Stock forecasting based on (gaussian) Hidden Markov Model',
    'long_description': None,
    'author': 'Martin Forejt',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
