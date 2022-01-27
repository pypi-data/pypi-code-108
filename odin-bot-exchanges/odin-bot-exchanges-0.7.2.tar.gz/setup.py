# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['odin_bot_exchanges',
 'odin_bot_exchanges.binance',
 'odin_bot_exchanges.kraken',
 'odin_bot_exchanges.orionx']

package_data = \
{'': ['*']}

install_requires = \
['binance-connector>=1.9.0,<2.0.0',
 'odin-bot-entities>=0.2.0,<0.3.0',
 'orionx-python-client>=0.4.0,<0.5.0',
 'python-dotenv>=0.19.1,<0.20.0']

setup_kwargs = {
    'name': 'odin-bot-exchanges',
    'version': '0.7.2',
    'description': '',
    'long_description': None,
    'author': 'adolfrodeno',
    'author_email': 'amvillalobos@uc.cl',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
