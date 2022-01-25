# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['kbackground']

package_data = \
{'': ['*']}

install_requires = \
['astropy>=4.2,<5.0',
 'matplotlib>=3.5.1,<4.0.0',
 'numpy>=1.19.4,<2.0.0',
 'patsy>=0.5.1,<0.6.0',
 'scipy>=1.5.4,<2.0.0']

setup_kwargs = {
    'name': 'kbackground',
    'version': '0.1.7',
    'description': '',
    'long_description': None,
    'author': 'Christina Hedges',
    'author_email': 'christina.l.hedges@nasa.gov',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.1,<4.0',
}


setup(**setup_kwargs)
