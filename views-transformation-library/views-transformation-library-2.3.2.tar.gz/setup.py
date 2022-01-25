# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['views_transformation_library']

package_data = \
{'': ['*']}

install_requires = \
['ingester3>=0.6.0',
 'pandas>=1.2.3,<2.0.0',
 'scikit_learn>=1.0.2,<2.0.0',
 'scipy>=1.6.2,<2.0.0',
 'stepshift>=1.2.0',
 'xarray>=0.19.0']

setup_kwargs = {
    'name': 'views-transformation-library',
    'version': '2.3.2',
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
