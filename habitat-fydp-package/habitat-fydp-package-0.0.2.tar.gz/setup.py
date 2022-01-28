# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['habitat_fydp_package']

package_data = \
{'': ['*']}

install_requires = \
['DateTime>=4.3,<5.0',
 'folium>=0.12.1,<0.13.0',
 'matplotlib>=3.5.1,<4.0.0',
 'numpy==1.17',
 'pandas==1',
 'pmdarima==1.5',
 'pyshp>=2.1.3,<3.0.0',
 'requests>=2.27.1,<3.0.0',
 'sklearn>=0.0,<0.1',
 'wwo-hist>=0.0.7,<0.0.8']

setup_kwargs = {
    'name': 'habitat-fydp-package',
    'version': '0.0.2',
    'description': 'Democratize access to HAB related data in Lake Erie to be used for scientific research',
    'long_description': '# habitat-fydp-package\n\n### Purpose of the Package\nDemocratize access to HAB related data in Lake Erie to be used for scientific research\n\n### Features\n\n### Getting Started\n\n### Usage \n\n### API References\n\n### Contribution \n\n### Author',
    'author': 'Shanthosh Pushparajah',
    'author_email': 'spushpar@uwaterloo.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/cognitetosh/habitat-fydp-package',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<3.8',
}


setup(**setup_kwargs)
