# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['luz']

package_data = \
{'': ['*']}

install_requires = \
['matplotlib>=3.3.2,<4.0.0',
 'pyee>=9.0.3,<10.0.0',
 'scipy>=1.7.2,<2.0.0',
 'torch>=1.7.0,<2.0.0']

setup_kwargs = {
    'name': 'luz',
    'version': '10.2.0',
    'description': 'Lightweight framework for structuring arbitrary reproducible neural network learning procedures using PyTorch.',
    'long_description': '==========\nLuz Module\n==========\n\n.. image:: https://codecov.io/gh/kijanac/luz/branch/main/graph/badge.svg\n  :target: https://codecov.io/gh/kijanac/luz\n\n.. image:: https://img.shields.io/badge/code%20style-black-000000.svg\n    :target: https://github\n\n**Lightweight framework for structuring arbitrary reproducible neural network learning procedures using PyTorch.**\n\nPyTorch code can easily become complex, unwieldy, and difficult to understand as a project develops. Luz aims to provide a common scaffold for PyTorch code in order to minimize boilerplate, maximize readability, and maintain the flexibility of PyTorch itself.\n\nThe basis of Luz is the Runner, an abstraction representing batch-wise processing of data over multiple epochs. Runner has predefined hooks to which code can be attached and a State which can be manipulated to define essentially arbitrary behavior. These hooks can be used to compose multiple Runners into a single algorithm, enabling dataset preprocessing, model testing, and other common tasks.\n\nTo further reduce boilerplate, the Learner abstraction is introduced as shorthand for the extremely common Preprocess-Train-Validate-Test algorithm. Simply inherit luz.Learner and define a handful of methods to completely customize your learning algorithm.\n\nTwo additional abstractions are provided for convenience: Scorers, which score (i.e. evaluate) a Learner according to some predefined procedure, and Tuners, which tune Learner hyperparameters. These abstractions provide a common interface which makes model selection a two-line process.\n\n---------------\nGetting Started\n---------------\n\nInstalling\n----------\nFrom `pip <https://pypi.org/project/luz/>`_:\n\n``pip install luz``\n\nFrom `conda <https://anaconda.org/kijana/luz>`_:\n\n``conda install -c conda-forge -c pytorch -c kijana luz``\n\nDocumentation\n-------------\nSee documentation `here <https://kijanac.github.io/luz/>`_.\n\nExamples\n--------\nSee example scripts in `Examples <https://github.com/kijanac/luz/tree/main/examples>`_.\n\n-------\nAuthors\n-------\nKi-Jana Carter\n\n-------\nLicense\n-------\nThis project is licensed under the MIT License - see the `LICENSE <https://github.com/kijanac/luz/blob/main/LICENSE>`_ file for details.\n\n------------\nContributing\n------------\nSee `CONTRIBUTING <https://github.com/kijanac/luz/blob/main/CONTRIBUTING.rst>`_.',
    'author': 'Ki-Jana Carter',
    'author_email': 'kijana@mit.edu',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/kijanac/luz',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<3.11',
}


setup(**setup_kwargs)
