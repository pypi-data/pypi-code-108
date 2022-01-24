# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pdme', 'pdme.measurement', 'pdme.model', 'pdme.util']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.21.1,<2.0.0', 'scipy>=1.5,<1.6']

setup_kwargs = {
    'name': 'pdme',
    'version': '0.4.1',
    'description': 'Python dipole model evaluator',
    'long_description': '# pdme - the python dipole model evaluator\n',
    'author': 'Deepak',
    'author_email': 'dmallubhotla+github@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.10',
}


setup(**setup_kwargs)
