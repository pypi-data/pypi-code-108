# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['xarray_multiscale']

package_data = \
{'': ['*']}

install_requires = \
['Jinja2>=3.0.3,<4.0.0',
 'dask>=2021.9.1,<2022.0.0',
 'mypy>=0.790,<0.791',
 'numpy>=1.19.4,<2.0.0',
 'scipy>=1.5.4,<2.0.0',
 'xarray>=0.17']

setup_kwargs = {
    'name': 'xarray-multiscale',
    'version': '0.2.3',
    'description': '',
    'long_description': None,
    'author': 'Davis Vann Bennett',
    'author_email': 'davis.v.bennett@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.1,<4',
}


setup(**setup_kwargs)
