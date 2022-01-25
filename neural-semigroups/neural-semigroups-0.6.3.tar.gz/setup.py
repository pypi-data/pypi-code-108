# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['neural_semigroups', 'neural_semigroups.datasets']

package_data = \
{'': ['*']}

install_requires = \
['pytorch-ignite', 'tensorboard', 'torch', 'tqdm']

setup_kwargs = {
    'name': 'neural-semigroups',
    'version': '0.6.3',
    'description': 'Neural networks powered research of semigroups',
    'long_description': '|Open In Colab| |PyPI version| |CircleCI| |Documentation Status|\n|codecov|\n\nNeural Semigroups\n=================\n\nThe project is abandoned.\n\nIf you want to reproduce results from the\n`paper <https://arxiv.org/abs/2103.07388>`__, please use `this\nnotebook <https://colab.research.google.com/github/inpefess/neural-semigroups/blob/master/examples/train_a_model.ipynb>`__.\n\nHere we try to model Cayley tables of semigroups using neural networks.\n\nThis work was inspired by `a sudoku\nsolver <https://github.com/Kyubyong/sudoku>`__. A solved Sudoku puzzle\nis nothing more than a Cayley table of a quasigroup from 9 items with\nsome well-known additional properties. So, one can imagine a puzzle made\nfrom a Cayley table of any other magma, e.g.\xa0a semigroup, by hiding part\nof its cells.\n\nThere are two major differences between sudoku and puzzles based on\nsemigroups:\n\n1) it’s easy to take a glance on a table to understand whether it is a\n   sudoku or not. That’s why it was possible to encode numbers in a\n   table cells as colour intensities. Sudoku is a picture, and a\n   semigroup is not. It’s difficult to check a Cayley table’s\n   associativity with a naked eye;\n\n2) Sudoku puzzles are solved by humans for fun and thus catalogued. When\n   solving a sudoku one knows for sure that there is a unique solution.\n   On the contrary, nobody guesses values in a partially filled Cayley\n   table of a semigroup as a form of amusement. As a result, one can\n   create a puzzle from a full Cayley table of a semigroup but there may\n   be many distinct solutions.\n\nHow to Install\n==============\n\nThe best way to install this package is to use ``pip``:\n\n.. code:: sh\n\n   pip install neural-semigroups\n\nHow to use\n==========\n\nThe simplest way to get started is to `use Google\nColaboratory <https://colab.research.google.com/github/inpefess/neural-semigroups/blob/master/examples/dae_4_colab.ipynb>`__.\n\nTo look at more experimental results for different semigroups\ncardinalities, you can use `Kaggle <https://kaggle.com>`__:\n\n-  `cardinality\n   4 <https://www.kaggle.com/inpefess/neural-semigroups-dae-dim-4>`__\n-  `cardinality\n   5 <https://www.kaggle.com/inpefess/neural-semigroups-dae-dim-5>`__\n\nThere is also an experimental\n`notebook <https://github.com/inpefess/neural-semigroups/blob/master/examples/ExperimentNotebook.ipynb>`__\ncontributed by `Žarko Bulić <https://github.com/zarebulic>`__.\n\nHow to Contribute\n=================\n\n`Pull requests <https://github.com/inpefess/neural-semigroups/pulls>`__\nare welcome. To start:\n\n.. code:: sh\n\n   git clone https://github.com/inpefess/neural-semigroups\n   cd neural-semigroups\n   # activate python virtual environment with Python 3.6+\n   pip install -U pip\n   pip install -U setuptools wheel poetry\n   poetry install\n   # recommended but not necessary\n   pre-commit install\n\nTo check the code quality before creating a pull request, one might run\nthe script\n`show_report.sh <https://colab.research.google.com/github/inpefess/neural-semigroups/blob/master/show_report.sh>`__.\nIt locally does nearly the same as the CI pipeline after the PR is\ncreated.\n\nReporting issues or problems with the software\n==============================================\n\nQuestions and bug reports are welcome on `the\ntracker <https://github.com/inpefess/neural-semigroups/issues>`__.\n\nMore documentation\n==================\n\nMore documentation can be found\n`here <https://neural-semigroups.readthedocs.io/en/latest>`__.\n\n.. |Open In Colab| image:: https://colab.research.google.com/assets/colab-badge.svg\n   :target: https://colab.research.google.com/github/inpefess/neural-semigroups/blob/master/examples/dae_4_colab.ipynb\n.. |PyPI version| image:: https://badge.fury.io/py/neural-semigroups.svg\n   :target: https://badge.fury.io/py/neural-semigroups\n.. |CircleCI| image:: https://circleci.com/gh/inpefess/neural-semigroups.svg?style=svg\n   :target: https://circleci.com/gh/inpefess/neural-semigroups\n.. |Documentation Status| image:: https://readthedocs.org/projects/neural-semigroups/badge/?version=latest\n   :target: https://neural-semigroups.readthedocs.io/en/latest/?badge=latest\n.. |codecov| image:: https://codecov.io/gh/inpefess/neural-semigroups/branch/master/graph/badge.svg\n   :target: https://codecov.io/gh/inpefess/neural-semigroups\n',
    'author': 'Boris Shminke',
    'author_email': 'boris@shminke.ml',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/inpefess/neural-semigroups',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.1,<3.10',
}


setup(**setup_kwargs)
