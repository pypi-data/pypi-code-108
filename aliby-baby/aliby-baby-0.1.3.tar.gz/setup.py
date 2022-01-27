# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['baby', 'baby.tracker', 'baby.training']

package_data = \
{'': ['*'],
 'baby': ['models/*'],
 'baby.training': ['.mypy_cache/3.7/*',
                   '.mypy_cache/3.7/_pytest/*',
                   '.mypy_cache/3.7/_pytest/_code/*',
                   '.mypy_cache/3.7/_pytest/_io/*',
                   '.mypy_cache/3.7/_pytest/assertion/*',
                   '.mypy_cache/3.7/_pytest/config/*',
                   '.mypy_cache/3.7/_pytest/mark/*',
                   '.mypy_cache/3.7/_typeshed/*',
                   '.mypy_cache/3.7/attr/*',
                   '.mypy_cache/3.7/baby/*',
                   '.mypy_cache/3.7/baby/training/*',
                   '.mypy_cache/3.7/collections/*',
                   '.mypy_cache/3.7/ctypes/*',
                   '.mypy_cache/3.7/email/*',
                   '.mypy_cache/3.7/importlib/*',
                   '.mypy_cache/3.7/importlib_metadata/*',
                   '.mypy_cache/3.7/iniconfig/*',
                   '.mypy_cache/3.7/json/*',
                   '.mypy_cache/3.7/logging/*',
                   '.mypy_cache/3.7/matplotlib/*',
                   '.mypy_cache/3.7/numpy/*',
                   '.mypy_cache/3.7/numpy/compat/*',
                   '.mypy_cache/3.7/numpy/core/*',
                   '.mypy_cache/3.7/numpy/distutils/*',
                   '.mypy_cache/3.7/numpy/fft/*',
                   '.mypy_cache/3.7/numpy/lib/*',
                   '.mypy_cache/3.7/numpy/matrixlib/*',
                   '.mypy_cache/3.7/numpy/polynomial/*',
                   '.mypy_cache/3.7/numpy/typing/*',
                   '.mypy_cache/3.7/os/*',
                   '.mypy_cache/3.7/packaging/*',
                   '.mypy_cache/3.7/pandas/*',
                   '.mypy_cache/3.7/pandas/core/*',
                   '.mypy_cache/3.7/pandas/core/arrays/*',
                   '.mypy_cache/3.7/pandas/core/dtypes/*',
                   '.mypy_cache/3.7/pandas/core/groupby/*',
                   '.mypy_cache/3.7/pandas/core/indexes/*',
                   '.mypy_cache/3.7/py/*',
                   '.mypy_cache/3.7/pytest/*',
                   '.mypy_cache/3.7/unittest/*',
                   '.mypy_cache/3.7/urllib/*']}

install_requires = \
['Pillow>=9.0.0,<10.0.0',
 'imageio==2.8.0',
 'matplotlib>=3.5.1,<4.0.0',
 'numpy>=1.21.4,<2.0.0',
 'pandas>=1.3.5,<2.0.0',
 'scikit-image>=0.19.1,<0.20.0',
 'scikit-learn==0.22.2.post1',
 'tensorflow>=2.1.4,<=2.3',
 'tqdm>=4.62.3,<5.0.0',
 'tune-sklearn>=0.4.1,<0.5.0',
 'xgboost==1.4.2']

setup_kwargs = {
    'name': 'aliby-baby',
    'version': '0.1.3',
    'description': 'Birth Annotator for Budding Yeast',
    'long_description': None,
    'author': 'Julian Pietsch',
    'author_email': 'jpietsch@ed.ac.uk',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.1,<3.11',
}


setup(**setup_kwargs)
