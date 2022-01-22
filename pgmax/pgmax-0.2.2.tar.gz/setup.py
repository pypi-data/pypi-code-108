# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pgmax', 'pgmax.bp', 'pgmax.fg']

package_data = \
{'': ['*']}

install_requires = \
['jax>=0.2.14,<0.3.0',
 'jaxlib>=0.1.67,<0.2.0',
 'joblib>=1.1.0,<2.0.0',
 'jupyter>=1.0.0,<2.0.0',
 'jupytext>=1.11.3,<2.0.0',
 'matplotlib>=3.2.0,<4.0.0',
 'numpy>=1.19.0,<2.0.0',
 'scikit-learn>=1.0.1,<2.0.0',
 'scipy>=1.2.3,<2.0.0',
 'tqdm>=4.61.0,<5.0.0']

extras_require = \
{'docs': ['sphinx>=3,<4']}

setup_kwargs = {
    'name': 'pgmax',
    'version': '0.2.2',
    'description': 'Loopy belief propagation for factor graphs on discrete variables, in JAX!',
    'long_description': '[![continuous-integration](https://github.com/vicariousinc/PGMax/actions/workflows/ci.yaml/badge.svg)](https://github.com/vicariousinc/PGMax/actions/workflows/ci.yaml)\n[![PyPI version](https://badge.fury.io/py/pgmax.svg)](https://badge.fury.io/py/pgmax)\n[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/vicariousinc/PGMax/master.svg)](https://results.pre-commit.ci/latest/github/vicariousinc/PGMax/master)\n[![codecov](https://codecov.io/gh/vicariousinc/PGMax/branch/master/graph/badge.svg?token=FrRlTDCFjk)](https://codecov.io/gh/vicariousinc/PGMax)\n[![Documentation Status](https://readthedocs.org/projects/pgmax/badge/?version=latest)](https://pgmax.readthedocs.io/en/latest/?badge=latest)\n\n# PGMax\n\nPGMax implements general factor graphs for discrete probabilistic graphical models (PGMs), and hardware-accelerated differentiable loopy belief propagation (LBP) in [JAX](https://jax.readthedocs.io/en/latest/).\n\n- **General factor graphs**: PGMax supports easy specification of general factor graphs with potentially complicated topology, factor definitions, and discrete variables with a varying number of states.\n- **LBP in JAX**: PGMax generates pure JAX functions implementing LBP for a given factor graph. The generated pure JAX functions run on modern accelerators (GPU/TPU), work with JAX transformations (e.g. `vmap` for processing batches of models/samples, `grad` for differentiating through the LBP iterative process), and can be easily used as part of a larger end-to-end differentiable system.\n\n[**Installation**](#installation)\n| [**Getting started**](#getting-started)\n\n## Installation\n\n### Install from PyPI\n```\npip install pgmax\n```\n\n### Install latest version from GitHub\n```\npip install git+https://github.com/vicariousinc/PGMax.git\n```\n\n### Developer\n```\ngit clone https://github.com/vicariousinc/PGMax.git\ncurl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py | python3 -\ncd PGMax\npoetry shell\npoetry install\npre-commit install\n```\n\n### Install on GPU\n\nBy default the above commands install JAX for CPU. If you have access to a GPU, follow the official instructions [here](https://github.com/google/jax#pip-installation-gpu-cuda) to install JAX for GPU.\n\n## Getting Started\n\nHere are a few self-contained Colab notebooks to help you get started on using PGMax:\n\n- [Tutorial on basic PGMax usage](https://colab.research.google.com/drive/1PQ9eVaOg336XzPqko-v_us3izEbjvWMW?usp=sharing)\n- [Implementing max-product LBP](https://colab.research.google.com/drive/1mSffrA1WgQwgIiJQd2pLULPa5YKAOJOX?usp=sharing) for [Recursive Cortical Networks](https://www.science.org/doi/10.1126/science.aag2612)\n- [End-to-end differentiable LBP for gradient-based PGM training](https://colab.research.google.com/drive/1yxDCLwhX0PVgFS7NHUcXG3ptMAY1CxMC?usp=sharing)\n\n\n\n## Citing PGMax\n\nTo cite this repository\n```\n@software{pgmax2021github,\n  author = {Guangyao Zhou* and Nishanth Kumar* and Miguel L\\’{a}zaro-Gredilla and Dileep George},\n  title = {{PGMax}: {F}actor graph on discrete variables and hardware-accelerated differentiable loopy belief propagation in {JAX}},\n  howpublished={\\url{http://github.com/vicariousinc/PGMax}},\n  version = {0.2.2},\n  year = {2022},\n}\n```\nwhere * indicates equal contribution.\n',
    'author': 'Stannis Zhou',
    'author_email': 'stannis@vicarious.com',
    'maintainer': 'Stannis Zhou',
    'maintainer_email': 'stannis@vicarious.com',
    'url': 'https://github.com/vicariousinc/PGMax',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<3.9',
}


setup(**setup_kwargs)
