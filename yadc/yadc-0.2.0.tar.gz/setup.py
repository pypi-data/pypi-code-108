# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['yadc']

package_data = \
{'': ['*']}

install_requires = \
['coloredlogs>=15.0.1,<16.0.0',
 'fake-useragent>=0.1.11,<0.2.0',
 'halo>=0.0.31,<0.0.32',
 'numpy>=1.21.4,<2.0.0',
 'psutil>=5.8.0,<6.0.0',
 'pydantic>=1.8.2,<2.0.0',
 'selenium>=4.0.0,<5.0.0']

entry_points = \
{'console_scripts': ['yadc = yadc.cli:main']}

setup_kwargs = {
    'name': 'yadc',
    'version': '0.2.0',
    'description': 'Yet Another DVSA Cancellation checker',
    'long_description': None,
    'author': 'John Maximilian',
    'author_email': '2e0byo@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<3.11',
}


setup(**setup_kwargs)
