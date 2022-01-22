# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['edr_agent_validator']

package_data = \
{'': ['*']}

install_requires = \
['desert>=2020.11.18,<2021.0.0',
 'marshmallow-enum>=1.5.1,<2.0.0',
 'marshmallow>=3.14.1,<4.0.0',
 'psutil>=5.9.0,<6.0.0',
 'typer>=0.4.0,<0.5.0']

entry_points = \
{'console_scripts': ['edr-agent-validator = edr_agent_validator.console:app']}

setup_kwargs = {
    'name': 'edr-agent-validator',
    'version': '0.2.0',
    'description': 'The Red Canary EDR validation tool.',
    'long_description': "This is an EDR agent validator project for the Red Canary Engineering Interview.\n\nI created this project using [Typer](https://typer.tiangolo.com/) and you can manage all it's dependencies with [Poetry](https://python-poetry.org/).\n\nIt's using [`psutil`](https://github.com/giampaolo/psutil) for cross platform process information gathering and uses [`desert`](https://desert.readthedocs.io/en/stable/) to serialize its dataclasses to logs (for activity tracking for correlation with EDR agents).\n\nThe arguments and defaults are all documented in the help menu. You can install it with pip via `pip install edr-agent-validator`.\n\nTry it out! By default all actions are appended as JSON to a file in the directory you run the tool in called `activity_log.txt`, but this can be configured.\n\nIt's a fairly simple tool, it uses the sockets api for it's network connections, basic python file I/O apis for file creation, modifying, and deletion, and the [`subprocess.Popen`](https://docs.python.org/3/library/subprocess.html#subprocess.Popen) api for launching a background process.\n\nFor the network activity component, it can send bytes over UDP or TCP.\n\nMost of the time I spent learning how to build an eloquent CLI with Typer and the new (to me) python type annotions. It was quite a fun learning exercise!\n\nOne thing to keep in mind about the activity logging is that during the printing/serialization of a dict, the key order is not consistent. This makes the logs more suited for parsing by machines than humans, as each line is it's own json object with it's keys in an arbitrary order. I'd probably improve this in the future to have a consistent serialization order.\n",
    'author': 'Andrew Kennedy',
    'author_email': 'andrewk36@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/andrew-kennedy/edr-agent-validator',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
