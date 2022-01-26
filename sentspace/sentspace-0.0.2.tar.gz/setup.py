# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sentspace',
 'sentspace.embedding',
 'sentspace.lexical',
 'sentspace.syntax',
 'sentspace.syntax.utils',
 'sentspace.utils']

package_data = \
{'': ['*'], 'sentspace': ['semantic/*', 'web/*']}

install_requires = \
['Morfessor>=2.0.6,<3.0.0',
 'PyICU>=2.8,<3.0',
 'PyYAML>=6.0,<7.0',
 'boto3>=1.20.25,<2.0.0',
 'nltk==3.6.2',
 'numpy>=1.22.1,<2.0.0',
 'pandas>=1.3.5,<2.0.0',
 'pdoc3>=0.10.0,<0.11.0',
 'polyglot>=16.7.4,<17.0.0',
 'pycld2>=0.41,<0.42',
 'scipy>=1.7.3,<2.0.0',
 'seaborn==0.11.2',
 'torch==1.9.0',
 'transformers==4.11.3']

setup_kwargs = {
    'name': 'sentspace',
    'version': '0.0.2',
    'description': '',
    'long_description': None,
    'author': 'Your Name',
    'author_email': 'you@example.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.10',
}


setup(**setup_kwargs)
