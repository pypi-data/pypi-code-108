# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['omicidx_sra', 'omicidx_sra.sra']

package_data = \
{'': ['*']}

install_requires = \
['pydantic>=1.9.0,<2.0.0', 'requests>=2.27.1,<3.0.0', 'ujson>=5.1.0,<6.0.0']

setup_kwargs = {
    'name': 'omicidx-sra',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Sean Davis',
    'author_email': 'seandavi@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
