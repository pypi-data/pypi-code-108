# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['datto', 'datto.data']

package_data = \
{'': ['*']}

install_requires = \
['black>=21.11b1,<22.0',
 'catboost>=1.0.3,<2.0.0',
 'gensim>=4.1.2,<5.0.0',
 'hypothesis>=6.24.5,<7.0.0',
 'isort>=5.10.1,<6.0.0',
 'jupyter-contrib-nbextensions>=0.5.1,<0.6.0',
 'jupytext>=1.13.1,<2.0.0',
 'lightgbm>=3.3.1,<4.0.0',
 'lime>=0.2.0,<0.3.0',
 'nbconvert>=6.3.0,<7.0.0',
 'nltk>=3.6.5,<4.0.0',
 'numpy>=1.21.4,<2.0.0',
 'pandas>=1.3.4,<2.0.0',
 'progressbar>=2.5,<3.0',
 'psycopg2-binary>=2.9.2,<3.0.0',
 'pytest>=6.2.5,<7.0.0',
 'python-json-logger>=2.0.2,<3.0.0',
 's3fs>=2021.11.0,<2022.0.0',
 'scikit-learn>=1.0.1,<2.0.0',
 'seaborn>=0.11.2,<0.12.0',
 'shap>=0.40.0,<0.41.0',
 'slack-client>=0.3.0,<0.4.0',
 'slack-sdk>=3.13.0,<4.0.0',
 'spacy>=3.2.0,<4.0.0',
 'sphinx-rtd-theme>=1.0.0,<2.0.0',
 'statsmodels>=0.13.1,<0.14.0',
 'tabulate>=0.8.9,<0.9.0',
 'wheel>=0.37.0,<0.38.0',
 'xgboost>=1.5.0,<2.0.0']

extras_require = \
{'docs': ['sphinx>=4.3.0,<5.0.0']}

setup_kwargs = {
    'name': 'datto',
    'version': '0.8.7',
    'description': 'Data Tools (Dat To)',
    'long_description': None,
    'author': 'kristiewirth',
    'author_email': 'kristie.ann.wirth@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7.1,<3.11',
}


setup(**setup_kwargs)
