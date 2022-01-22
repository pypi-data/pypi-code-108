# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['jaffalearn', 'jaffalearn.data']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.21.4,<2.0.0',
 'pandas>=1.3.4,<2.0.0',
 'tensorboard>=2.7.0,<3.0.0',
 'torch>=1.8.1,<2.0.0',
 'torchaudio>=0.8.1,<0.9.0',
 'tqdm>=4.62.3,<5.0.0']

setup_kwargs = {
    'name': 'jaffalearn',
    'version': '0.2.0',
    'description': 'A PyTorch-based ML framework with a focus on audio classification problems',
    'long_description': None,
    'author': 'Turab Iqbal',
    'author_email': 't.iqbal@surrey.ac.uk',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/tqbl/jaffalearn',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
