# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['jps_algo', 'jps_algo.utils']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'jps-algo',
    'version': '0.1.0',
    'description': "Jackson's Preemptive Scheduleを解くためのアルゴリズムが実装されている",
    'long_description': None,
    'author': '鈴木貴大',
    'author_email': 'merioda.seven.24@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/tkp0331/jps-algo',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7.9,<4.0.0',
}


setup(**setup_kwargs)
