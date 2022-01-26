# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pie_sensor']

package_data = \
{'': ['*']}

install_requires = \
['Adafruit-Blinka>=6.17.0,<7.0.0',
 'adafruit-circuitpython-dht>=3.7.0,<4.0.0',
 'gpiozero>=1.6.2,<2.0.0',
 'prometheus-client>=0.12.0,<0.13.0']

setup_kwargs = {
    'name': 'pie-sensor',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'HBartha',
    'author_email': 'hunor.bartha@frequentis.frq',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
