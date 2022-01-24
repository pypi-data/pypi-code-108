# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['envo']

package_data = \
{'': ['*'], 'envo': ['templates/*']}

install_requires = \
['colorama',
 'envium>=1.0.0,<2.0.0',
 'fire>=0,<1',
 'globmatch>=2,<3',
 'loguru>=0,<1',
 'prompt_toolkit>=3,<4',
 'pygments>=2,<3',
 'rhei>=0,<1',
 'rich',
 'watchdog>=2,<3',
 'xonsh==0.9.27']

extras_require = \
{':python_version < "3.8"': ['typing-extensions>=3.7.4,<4.0.0'],
 ':python_version >= "3.6" and python_version < "3.7"': ['dataclasses>=0.7,<0.9']}

entry_points = \
{'console_scripts': ['envo = envo.scripts:_main']}

setup_kwargs = {
    'name': 'envo',
    'version': '1.1.3',
    'description': 'Smart Environments handling - Define command hooks, file hooks and env variables in python and activate hot reloaded shells.',
    'long_description': '===========================================\nenvo - smart environment variables handling\n===========================================\n\nDefine environmental variables in python and activate hot reloaded shells for them.\n\nFeatures\n--------\n* Initialisation of variables in a given directory (creates common variables file too)\n\n.. code-block::\n\n    user@pc:/project$ envo local --init  # creates local environment python files\n\n* Easy and dynamic handling in .py files (See documentation to learn more)\n* Provides addons like handling virtual environments\n\n.. code-block::\n\n    user@pc:/project$ envo local --init=venv  # will add .venv to PATH\n\n* Automatic env variables generation based on defined python variables\n* Hot reload. Activated shell will reload environmental variables when files change.\n* Activating shells for a given environment\n\n.. code-block::\n\n    user@pc:/project$ envo local\n    🐣(project)user@pc:/project$\n    🐣(project)user@pc:/project$ exit\n    user@pc:/project$ envo prod\n    🔥(project)user@pc:/project$\n\n\n* Saving variables to a regular .env file\n\n.. code-block::\n\n    user@pc:/project$ envo local --save\n\n* Printing variables (handy for non interactive CLIs like CI or docker)\n\n.. code-block::\n\n    user@pc:/project$ envo local --dry-run\n\n* Detects undefined variables.\n* Perfect for switching kubernetes contexts and devops tasks\n\n\nExample\n#######\nInitialising environment\n\n.. code-block::\n\n    user@pc:/project$ envo local --init\n\n\nWill create :code:`env_comm.py` and :code:`env_local.py`\n\n.. code-block:: python\n\n    # env_comm.py\n    @dataclass\n    class ProjectEnvComm(Env):\n        @dataclass\n        class Python(BaseEnv):\n            version: str\n\n        class Meta:\n            raw = ["kubeconfig"]  # disable namespacing\n\n        python: Python\n        number: int\n        kubeconfig: Path\n        # Add more variables here\n\n        def __init__(self) -> None:\n            super().__init__(root=Path(os.path.realpath(__file__)).parent)\n            self.name = "proj"\n            self.python = self.Python(version="3.8.2")\n            self.kubeconfig = self.root / f"{self.stage}/kubeconfig.yaml"\n\n    # env_local.py\n    @dataclass\n    class ProjectEnv(ProjectEnvComm):\n        def __init__(self) -> None:\n            self.stage = "test"\n            self.emoji = "🛠️"\n            super().__init__()\n\n            self.number = 12\n\n    Env = ProjectEnv\n\nExample usage:\n\n.. code-block::\n\n    user@pc:/project$ envo  # short for "envo local"\n    🐣(project)user@pc:/project$ echo $PROJ_PYTHON_VERSION\n    3.8.2\n    🐣(project)user@pc:/project$echo $PROJ_NUMBER\n    12\n\n\nTODO:\nMajor:\n* Refactor start_in\n* Add file hooks\n* Add bootstrap (versioning etc)\n* add error line number\n\nMinor:\n* Shell should highlight envo commands on green\n* Unnecessary prompt rendered again aftet Ctr-d (only on xonsh?)\n* work on public/private fields and methods\n* add examples\n* print hooks for repr\n* Add reload command\n\nBugs:\n* exiting while env loading yields Attribute Error\n\nImprovements:\n* type checking ?\n',
    'author': 'Damian Krystkiewicz',
    'author_email': 'damian.krystkiewicz@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.6.2,<4.0',
}


setup(**setup_kwargs)
