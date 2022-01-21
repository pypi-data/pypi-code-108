# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['py_progress_tracker']

package_data = \
{'': ['*']}

install_requires = \
['colorama>=0.4.4,<0.5.0',
 'psutil>=5.8.0,<6.0.0',
 'py-cpuinfo>=8.0.0,<9.0.0',
 'tabulate>=0.8.9,<0.9.0',
 'termcolor>=1.1.0,<2.0.0']

setup_kwargs = {
    'name': 'py-progress-tracker',
    'version': '0.4.1',
    'description': 'A simple benchmarking library',
    'long_description': None,
    'author': 'Zama',
    'author_email': 'hello@zama.ai',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
