# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['quaterion_models',
 'quaterion_models.encoders',
 'quaterion_models.encoders.extras',
 'quaterion_models.heads',
 'quaterion_models.types',
 'quaterion_models.utils']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.21.2,<2.0.0', 'torch>=1.8.2']

extras_require = \
{'fasttext': ['gensim>=4.1.2,<5.0.0']}

setup_kwargs = {
    'name': 'quaterion-models',
    'version': '0.1.2',
    'description': 'The collection of building blocks building fine-tunable metric learning models',
    'long_description': '# Quaterion-models\n\nThe collection of building blocks building fine-tunable metric learning models.\n\n',
    'author': 'generall',
    'author_email': 'andrey@vasnetsov.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/qdrant/quaterion-models',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<3.10',
}


setup(**setup_kwargs)
