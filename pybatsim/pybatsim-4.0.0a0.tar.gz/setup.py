# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['pybatsim',
 'pybatsim.batsim',
 'pybatsim.batsim.cmds',
 'pybatsim.batsim.tools',
 'pybatsim.schedulers',
 'pybatsim.schedulers.unMaintained']

package_data = \
{'': ['*']}

install_requires = \
['docopt>=0.6.2,<0.7.0',
 'procset>=1.0,<2.0',
 'pyzmq>=22.0.3,<23.0.0',
 'sortedcontainers>=2.3.0,<3.0.0']

extras_require = \
{':python_version < "3.10"': ['importlib-metadata>=3.6']}

entry_points = \
{'console_scripts': ['pybatsim = pybatsim.cmdline:main',
                     'pybatsim-experiment = '
                     'pybatsim.batsim.cmds.experiments:main',
                     'pybatsim-legacy = pybatsim.batsim.cmds.launcher:main'],
 'pybatsim.schedulers': ['backfill-easy = '
                         'pybatsim.schedulers.easyBackfill:EasyBackfill',
                         'fcfs-sleeper = '
                         'pybatsim.schedulers.fcfsSchedSleep:FcfsSchedSleep',
                         'filler = pybatsim.schedulers.fillerSched:FillerSched',
                         'filler-events = '
                         'pybatsim.schedulers.fillerSchedWithEvents:FillerSchedWithEvents',
                         'random = '
                         'pybatsim.schedulers.randomSched:RandomSched']}

setup_kwargs = {
    'name': 'pybatsim',
    'version': '4.0.0a0',
    'description': 'Python API and schedulers for Batsim',
    'long_description': '\n===============================\nPybatsim\n===============================\n\nPyBatsim helps you developing your own scheduler in python!\n\nThe library consists of two layers:\n\n1. The low level API `batsim.batsim` which handles the communication with the\n   Batsim instance (example scheduler: `schedulers/fillerSched.py`).\n2. The high level API `batsim.sched` which contains an object oriented abstraction layer\n   to provide a simpler API for accessing data from Batsim and filtering for\n   jobs and resources (example scheduler: `schedulers/delayProfilesAsTasks.py`).\n\nCommands\n--------\n\nThe following commands are provided:\n\n*pybatsim*\n    To launch schedulers\n\n*pybatsim-experiment*\n    To launch experiments.\n    See `sample.expe.json` for an example configuration file expected by this launcher.\n    The launcher will start Batsim and the scheduler with the correct options.\n\n*pybatsim-postprocess-jobs*\n    To manipulate the `out_jobs.csv` file based on data only available in the\n    scheduler but not in Batsim.\n\nBatsim Version Compatibilities\n------------------------------\n\nAs there are different release paces between Batsim and Pybatsim versions, here is a list of compatibilities between the two projects:\n\n    - `Batsim master branch`_ with `Pybatsim master branch`_ (development branches, may be unstable)\n    - `Batsim v3_0_0`_ with `Pybatsim v3_0_0`_ (latest major release, stable)\n    - `Batsim v2_0_0`_ with `Pybatsim batsim_2_0_compatible`_\n\nMoreover, all notable changes are listed in the `changelog <https://gitlab.inria.fr/batsim/pybatsim/blob/master/CHANGELOG.rst>`_.\n\nExamples\n--------\n\nStart a scheduler\n~~~~~~~~~~~~~~~~~\n\nSee the *schedulers* directory for the available built-in schedulers.\nA simple built-in scheduler instance can be executed by calling::\n\n  pybatsim fillerSched\n\nThis command, however, requires an already running Batsim instance.\n\nThe parameter to `pybatsim` can also be a file outside of the project directory\nlike::\n\n  pybatsim path/to/scheduler.py\n\nSchedulers of the higher level API (`batsim.sched`) can be executed in the same way::\n\n  pybatsim delayProfilesAsTasks\n\nThis example scheduler will make use of dynamic jobs and convert delay jobs into tasks.\nNote that dynamic job submissions have to be enabled in your running Batsim instance to be able to use this scheduler.\n\nTo see all available starting options see also::\n\n  pybatsim --help\n\nRun an experiment\n~~~~~~~~~~~~~~~~~\n\nTo run a complete experiment the experiment launcher can be used::\n\n  pybatsim-experiment --verbose sample.expe.json\n\nPlease note that Batsim has to be installed and the environment has to be set-up for this command to succeed.\n\nFiles\n-----\n\n*sample.expe.json*\n    See `launch_expe.json`\n\n*batsim/batsim.py*\n    This class helps you communicate with the batsim server\n\n*batsim/sched/*\n    High level scheduler API\n\n*batsim/tools/*\n    Tools to start the schedulers or for working with the generated data\n\n*schedulers/*\n    Contains all the schedulers. Schedulers name should follow this convention:\n    `fooBar.py` contains the `FooBar` classname which has as an ancestor `batsim.batsim.BatsimScheduler`.\n\n*schedulers/fillerSched.py*\n    A kind of first fit without topology scheduler\n\n*schedulers/easyBackfill.py*\n    EASY backfilling where jobs are seen as rectangles\n\n*schedulers/delayProfilesAsTasks.py*\n    A scheduler using the high level scheduler API to split big delay jobs into\n    small tasks.\n\nInstallation\n------------\n\nYou can install, upgrade, uninstall PyBatsim with these commands::\n\n  pip install [--user] pybatsim\n  pip install [--user] --upgrade pybatsim\n  pip uninstall pybatsim\n\nDocumentation\n-------------\n\nTo generate the html documentation use the setup target::\n\n  ./setup.py doc\n\nTesting\n-------\n\nTo run the test experiments it is preferable to first enter in a nix shell specific for the pybatsim development with the following command::\n\n  nix-shell https://github.com/oar-team/kapack/archive/master.tar.gz -A pybatsim_dev\n\nThen you can run tests with the setup target::\n\n  ./setup.py test --batsim-bin=path/to/batsim/binary\n\n\n.. _Batsim master branch: https://gitlab.inria.fr/batsim/batsim/tree/master\n.. _Pybatsim master branch: https://gitlab.inria.fr/batsim/pybatsim/tree/master\n.. _Batsim v3_0_0: https://gitlab.inria.fr/batsim/batsim/tags/v3.0.0\n.. _Pybatsim v3_0_0: https://gitlab.inria.fr/batsim/pybatsim/tags/v3.0.0\n.. _Batsim v2_0_0: https://gitlab.inria.fr/batsim/batsim/tags/v2.0.0\n.. _Pybatsim batsim_2_0_compatible: https://gitlab.inria.fr/batsim/pybatsim/tags/batsim_2.0_compatible\n',
    'author': 'Henri Casanova',
    'author_email': 'henric@hawaii.edu',
    'maintainer': 'Raphaël Bleuse',
    'maintainer_email': 'raphael.bleuse@inria.fr',
    'url': 'https://gitlab.inria.fr/batsim/pybatsim',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7.1,<4.0.0',
}


setup(**setup_kwargs)
