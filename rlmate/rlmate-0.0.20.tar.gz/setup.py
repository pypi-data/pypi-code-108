# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['rlmate', 'rlmate.core', 'rlmate.networks']

package_data = \
{'': ['*']}

install_requires = \
['GitPython>=3.1.24,<4.0.0',
 'leb128>=1.0.4,<2.0.0',
 'matplotlib>=3.4.3,<4.0.0',
 'numpy',
 'pandas>=1.3.4,<2.0.0',
 'python-telegram-bot>=13.6,<14.0',
 'torch==1.9.1']

entry_points = \
{'console_scripts': ['hermes = rlmate.hermes:main']}

setup_kwargs = {
    'name': 'rlmate',
    'version': '0.0.20',
    'description': 'tbd.',
    'long_description': "# RLMate\n\nProject under development. \n\nThe RLMate is a package designed to take over parts of Reinforcement Learning that are needed frequently. \nIt comes together with the command line tool 'Hermes'. \n\nThe idea is to have a tool\n- to organize RL tasks and carry out several scripts,\n- to execute common RL tasks, e.g., plot training curves, \n- have commonly shared code as a python package instead of reimplementing it over and over again.  \n\n\n## Installation\nSimply install the current version with\n* `pip install  rlmate`\n\nFurther instructions will be added when the package involves. \n\n\n## Installation\n\ntodo\n## Command Line Tool\n\nAll available commands can also be seen by using the help function `hermes -h`\n\nAvailable commands:\n* ``exec -f file``: execute the specified Hermesfile. \n* ``exec -e command``: execute the specified command. __Not supported yet!__\n* ``exec -n name``: give the execution file a name to make the results directory more human readable.\n* ``create``: create an example Hermes files\n* ``help command``: show a detailed help of the specified command.\n* `-ho`: show help for hermes options used in .hermes files (also see below) \n\n### Settings\nSettings in this context means something that is not set for a particular execution/hermesfile, but for the __git repository__ that is currently used. \nThe settings are saved in the root if the repository in the ``.hermes_settings`` file. \nThe current settings (with the default value if there is no settings file) are:\n* `path_to_experiment ('./')`: specifies the path where to store the results of the experiment in. Takes the repository root as entry point.\n* `threads (1)`: specifies how many of the specified jobs should be executed parallel.\n\nThe syntax is as follow: `setting:value` and only one setting should be specified per line.\n\n### Hermes-options \nFor each job, different Hermes options can be specified. Currently, these options are:\n* `-ca file`: the `file` is copied to the experiment folder after the execution of the job.\n* `-cb file`: the `file` is copied to the experiment folder before the execution of the job.\n* `-ma file`: the `file` is moved to the experiment folder after the execution of the job.\n* `-l/--log (True | False)`: if `True` the stdout and stderr of the job will not be printed to console, but stored in log files. Defaults to `True`.\n* `-m`: if set, a telegram message will be sent to the chat_ids specified in the `.hermes_settings` file. \n\n\n### Hermesfile\n\nThe Hermesfile specifies the experiments that should be ran. \nHermesfiles have the ending `.hermes`.\nEach file is divided into 3 parts:\n\n#### 1. PRE\nIn the PRE part of the Hermesfile, the settings can be adjustet *for the given Hermesfile only*.\nSo if you generally want to process the files by using two threads, and thereforce specified so in the `.hermes_settings` file, you can change this for the current hermesfile only by specifying it in the PRE section. \nThis is done linewise per setting. \nThe syntax is the same as for the settings file.  \n\n#### 2. STD-H\nSometimes, some Hermes options should be applied to all jobs of the Hermes file. \nHermes-options specified in the STD-H section will be applied to all jobs. \nThe syntax is one Hermes-option per line with `-flag file`\n\n#### 3. STD-E\nAlso, there sometimes are script arguments that should be applied to all jobs while just a few are about to be varied. \nSuch arguments specified in the STD-E section will be applied to all jobs. \nThe syntax in one argument per line, e.g. `-ne 100` or `-n`.\n\nThis standard arguments will be added _before_ the arguments specified in the exec lines. \nNote that this order may be important for your script. \n#### 4. EXEC\nIn this section the jobs are specified with the following syntax:\n```\n[[cmd],[Hermes-options]]\n```\nwhereby the Hermes-options are separated by comma.\nIn each line, one job can be specified. \nAll settings that should be saved automatically must be set in the cmd. \n### Storage\n\nAll files will be saved in the directory `experiments/script_name/uniqe_name`, where\n* `script_name` is the name of the script specified in the job\n* `unique_name` is the unique combination of date and time, commit number, and name that may have been specified with the `-n` flag\n\nand the experiments directory will be created on the first call in the directory as specified in the settings. \n\nIf during the execution of the script new files or directories will be created, they are automatically moved to the storage if they include the `unique_name`. \nHow this name is given to the script will be specified in the next section. \n\nAdditionally, in the future there will be an overview file giving detailed information about all the made experiments. \n\n\n\n### Script Compatibility\nFor your script to be compatible with Hermes, there are basically two things you need to consider:\n1. All the parameters that should be saved must be specified by command line. \nIf you want to save additional parameters, make sure to specify it by archiving the files by using the Hermes-options.\n2. This is the only strong requirement: The first argument of the executed script must be the unique name, that is determined by Hermes. \nYou must not do anything with that identifier except for saving additional files as specified in the Storage section.\n\n",
    'author': 'Timo P. Gros',
    'author_email': 'timopgros@cs.uni-saarland.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
