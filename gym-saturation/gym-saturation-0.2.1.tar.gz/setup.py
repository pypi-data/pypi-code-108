# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['gym_saturation',
 'gym_saturation.envs',
 'gym_saturation.logic_ops',
 'gym_saturation.parsing']

package_data = \
{'': ['*'],
 'gym_saturation': ['resources/*',
                    'resources/TPTP-mock/Axioms/*',
                    'resources/TPTP-mock/Problems/SET/*',
                    'resources/TPTP-mock/Problems/TST/*']}

install_requires = \
['gym', 'lark-parser']

extras_require = \
{':python_version < "3.9"': ['importlib_resources']}

setup_kwargs = {
    'name': 'gym-saturation',
    'version': '0.2.1',
    'description': 'An OpenAI Gym environment for saturation provers',
    'long_description': '..\n  Copyright 2021-2022 Boris Shminke\n\n  Licensed under the Apache License, Version 2.0 (the "License");\n  you may not use this file except in compliance with the License.\n  You may obtain a copy of the License at\n\n      https://www.apache.org/licenses/LICENSE-2.0\n\n  Unless required by applicable law or agreed to in writing, software\n  distributed under the License is distributed on an "AS IS" BASIS,\n  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.\n  See the License for the specific language governing permissions and\n  limitations under the License.\n\n|PyPI version| |CircleCI| |Documentation Status| |codecov| |Binder|\n\ngym-saturation\n==============\n\n``gym-saturation`` is an `OpenAI Gym <https://gym.openai.com/>`__\nenvironment for reinforcement learning (RL) agents capable of proving\ntheorems. Currently, only theorems written in `TPTP\nlibrary <http://tptp.org>`__ formal language in clausal normal form\n(CNF) are supported. ``gym-saturation`` implements the ‘given clause’\nalgorithm (similar to one used in\n`Vampire <https://github.com/vprover/vampire>`__ and `E\nProver <https://github.com/eprover/eprover>`__). Being written in\nPython, ``gym-saturation`` was inspired by\n`PyRes <https://github.com/eprover/PyRes>`__. In contrast to monolithic\narchitecture of a typical Automated Theorem Prover (ATP),\n``gym-saturation`` gives different agents opportunities to select\nclauses themselves and train from their experience. Combined with a\nparticular agent, ``gym-saturation`` can work as an ATP.\n\n``gym-saturation`` can be interesting for RL practitioners willing to\napply their experience to theorem proving without coding all the\nlogic-related stuff themselves. It also can be useful for automated\ndeduction researchers who want to create an RL-empowered ATP.\n\nHow to Install\n==============\n\nThe best way to install this package is to use ``pip``:\n\n.. code:: sh\n\n   pip install gym-saturation\n\nOne can also run it in a Docker container:\n\n.. code:: sh\n\n   docker build -t gym-saturation https://github.com/inpefess/gym-saturation.git\n   docker run -it --rm -p 8888:8888 gym-saturation jupyter-lab --ip=0.0.0.0 --port=8888 --no-browser\n\nHow to use\n==========\n\nSee `the\nnotebook <https://github.com/inpefess/gym-saturation/blob/master/examples/example.ipynb>`__\nor run it in\n`Binder <https://mybinder.org/v2/gh/inpefess/gym-saturation/HEAD?labpath=example.ipynb>`__\nfor more information.\n\nHow to Contribute\n=================\n\n`Pull requests <https://github.com/inpefess/gym-saturation/pulls>`__ are\nwelcome. To start:\n\n.. code:: sh\n\n   git clone https://github.com/inpefess/gym-saturation\n   cd gym-saturation\n   # activate python virtual environment with Python 3.6+\n   pip install -U pip\n   pip install -U setuptools wheel poetry\n   poetry install\n   # recommended but not necessary\n   pre-commit install\n\nAll the tests in this package are\n`doctests <https://docs.python.org/3/library/doctest.html>`__. One can\nrun them with the following command:\n\n.. code:: sh\n\n   pytest --doctest-modules gym-saturation\n\nTo check the code quality before creating a pull request, one might run\nthe script ``local-build.sh``. It locally does nearly the same as the CI\npipeline after the PR is created.\n\nReporting issues or problems with the software\n==============================================\n\nQuestions and bug reports are welcome on `the\ntracker <https://github.com/inpefess/gym-saturation/issues>`__.\n\nMore documentation\n==================\n\nMore documentation can be found\n`here <https://gym-saturation.readthedocs.io/en/latest>`__.\n\n.. |PyPI version| image:: https://badge.fury.io/py/gym-saturation.svg\n   :target: https://badge.fury.io/py/gym-saturation\n.. |CircleCI| image:: https://circleci.com/gh/inpefess/gym-saturation.svg?style=svg\n   :target: https://circleci.com/gh/inpefess/gym-saturation\n.. |Documentation Status| image:: https://readthedocs.org/projects/gym-saturation/badge/?version=latest\n   :target: https://gym-saturation.readthedocs.io/en/latest/?badge=latest\n.. |codecov| image:: https://codecov.io/gh/inpefess/gym-saturation/branch/master/graph/badge.svg\n   :target: https://codecov.io/gh/inpefess/gym-saturation\n.. |Binder| image:: https://mybinder.org/badge_logo.svg\n   :target: https://mybinder.org/v2/gh/inpefess/gym-saturation/HEAD?labpath=example.ipynb\n',
    'author': 'Boris Shminke',
    'author_email': 'boris@shminke.ml',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/inpefess/gym-saturation',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7.1,<3.11',
}


setup(**setup_kwargs)
