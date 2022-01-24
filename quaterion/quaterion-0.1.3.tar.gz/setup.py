# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['quaterion',
 'quaterion.dataset',
 'quaterion.eval',
 'quaterion.loss',
 'quaterion.train',
 'quaterion.train.encoders',
 'quaterion.utils']

package_data = \
{'': ['*']}

install_requires = \
['loguru>=0.5.3,<0.6.0',
 'pytorch-lightning>=1.5.8,<2.0.0',
 'quaterion-models>=0.1.1',
 'torch>=1.8.2']

setup_kwargs = {
    'name': 'quaterion',
    'version': '0.1.3',
    'description': 'Metric Learning fine-tuning framework',
    'long_description': "# Quaterion\n\n>  A dwarf on a giant's shoulders sees farther of the two \n\nA tool collection and framework for fine-tuning metric learning model. \n",
    'author': 'generall',
    'author_email': 'andrey@vasnetsov.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/qdrant/quaterion',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<3.10',
}


setup(**setup_kwargs)
