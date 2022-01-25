# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pythonsdm']

package_data = \
{'': ['*']}

install_requires = \
['fire>=0.4.0,<0.5.0',
 'numpy>=1.22.1,<2.0.0',
 'scikit-image>=0.19.1,<0.20.0',
 'scikit-learn>=1.0.2,<2.0.0',
 'tqdm>=4.62.3,<5.0.0']

entry_points = \
{'console_scripts': ['sdm-test = pythonsdm:test',
                     'sdm-train = pythonsdm:train']}

setup_kwargs = {
    'name': 'pythonsdm',
    'version': '0.3.0',
    'description': 'Supervised Descent Method and its Applications to Face Alignment',
    'long_description': None,
    'author': 'Gilad Kutiel',
    'author_email': 'gilad.kutiel@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
