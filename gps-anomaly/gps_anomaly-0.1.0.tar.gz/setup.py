# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['gps_anomaly']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'gps-anomaly',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'mcv_',
    'author_email': 'murat@visiosoft.com.tr',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
