# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sco_py', 'sco_py.sco_gurobi', 'sco_py.sco_osqp']

package_data = \
{'': ['*']}

install_requires = \
['gurobipy>=9.0.0,<9.2.0',
 'numdifftools>=0.9.40,<0.10.0',
 'numpy>=1.21.4,<2.0.0',
 'osqp>=0.6.2,<0.7.0',
 'pytest>=6.2.5,<7.0.0',
 'scipy>=1.7.2,<2.0.0']

setup_kwargs = {
    'name': 'sco-py',
    'version': '0.2.0',
    'description': 'A Sequential Convex Optimization library for solving non-convex optimization problems. Intended for use with the OpenTAMP planning system.',
    'long_description': "[![continuous-integration](https://github.com/Algorithmic-Alignment-Lab/sco_py/actions/workflows/ci.yaml/badge.svg)](https://github.com/Algorithmic-Alignment-Lab/sco_py/actions/workflows/ci.yaml) [![PyPI version](https://badge.fury.io/py/sco-py.svg)](https://badge.fury.io/py/sco-py)\n\n# sco_py: Sequential Convex Optimization with Python\nsco_py is a lightweight Sequential Convex Optimization library for solving non-convex optimization problems. sco_py is intended for use with the OpenTAMP planning system. Currently, the library supports both [Gurobi](https://www.gurobi.com/) (license required) and [OSQP](https://osqp.org/) (open-source, no license required!) as backend QP solvers.\n\n## Installation\n### From PyPI with pip\nSimply run: `pip install sco-py`\n\n### From GitHub with pip\nSimply run: `pip install git+https://github.com/Algorithmic-Alignment-Lab/sco_py.git`\n\n### Developer (from source)\n1. Clone this repository [from GitHub](https://github.com/Algorithmic-Alignment-Lab/sco_py)\n1. Install Poetry by following the instructions from [here](https://python-poetry.org/docs/#installation)\n1. Install all dependencies with `poetry install`.\n\n## Contributing\nsco is an open-source repository and as such, we welcome contributions from interested members of the community! If you have a new idea for a feature/contribution, do post in the ['Discussions' tab of the GitHub repository](https://github.com/Algorithmic-Alignment-Lab/sco_py/discussions) to get some feedback from the maintainers before starting development. In general, we recommend that you fork the main repository, create a new branch with your proposed change, then open a pull-request into the main repository. The main requirement for a new feature is that it cannot break the current test cases (see below for how to run our tests) unless this is unavoidable, and in this case, it should modify/introduce new tests as necessary. In particular, we welcome updates to documentation (docstrings, comments, etc. that make the codem more approachable for new users) and test cases!\n\n### Running tests\nIf you do not have a license for Gurobi, then you can only run the OSQP tests. To do so, run:\n```\npytest tests/sco_osqp/\n```\nIf you do have a license for Gurobi, then you can run all tests with the `pytest` command.\n\nNote that our Contrinuous Integration (CI) setup only checks and reports status for OSQP tests. In general, if you are contributing a new feature, it *must* pass the existing OSQP tests and contribute new tests that test the new feature at least with OSQP (and preferably with Gurobi as well).",
    'author': 'Nishanth Kumar',
    'author_email': 'njk@csail.mit.edu',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<3.11',
}


setup(**setup_kwargs)
