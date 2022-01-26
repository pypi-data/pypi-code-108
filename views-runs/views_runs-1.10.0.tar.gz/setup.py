# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['views_runs']

package_data = \
{'': ['*']}

install_requires = \
['scikit-learn>=1.0.2,<2.0.0',
 'stepshift>=2.2.0,<2.3.0',
 'views-partitioning>=3.0.0,<4.0.0',
 'viewser>=5.9.0,<6.0.0']

setup_kwargs = {
    'name': 'views-runs',
    'version': '1.10.0',
    'description': '',
    'long_description': None,
    'author': 'peder2911',
    'author_email': 'pglandsverk@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.10',
}


setup(**setup_kwargs)
