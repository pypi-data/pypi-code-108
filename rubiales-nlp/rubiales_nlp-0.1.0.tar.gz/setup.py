# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['rubiales_nlp']

package_data = \
{'': ['*']}

install_requires = \
['black>=21.12b0,<22.0',
 'flake8>=4.0.1,<5.0.0',
 'nltk>=3.6.7,<4.0.0',
 'spacy>=3.2.1,<4.0.0']

setup_kwargs = {
    'name': 'rubiales-nlp',
    'version': '0.1.0',
    'description': 'Solve NLP common tasks',
    'long_description': '# Rubiales NLP\n\nThis is a module for standarize the problems that appear in NLP projects\n',
    'author': 'Alberto Rubiales',
    'author_email': 'al.rubiales.b@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<=3.10',
}


setup(**setup_kwargs)
