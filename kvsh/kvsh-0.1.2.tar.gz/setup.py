# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['kvsh']

package_data = \
{'': ['*']}

install_requires = \
['argcomplete>=1.12.3,<2.0.0',
 'argparse>=1.4.0,<2.0.0',
 'dataclasses-json>=0.5.6,<0.6.0',
 'jsonschema>=4.2.1,<5.0.0',
 'logging-actions>=0.1.6,<0.2.0',
 'xdg>=5.1.1,<6.0.0']

entry_points = \
{'console_scripts': ['kv = kvsh:kv', 'kvv = kvsh:kvv']}

setup_kwargs = {
    'name': 'kvsh',
    'version': '0.1.2',
    'description': 'Persistent key-value store for the command line',
    'long_description': '# kvsh, a command-line key-value store for the shell\n- Cross-shell persistence\n- Easy UI, with tab completion\n## `kv` for quick operations\n```shell\n$ kv hello world\n$ kv hello\nworld\n```\n## `kvv` for advanced functionality\n```shell\n$ kv hello world\n$ kv foo food\n$ kv bar bartender\n$ kvv env # Print key=value iff key is a valid environment variable name\nhello=world\nfoo=food\nbar=bartender\n$ kvv remove hello\n$ kvv env\nhello=world\n$ kvv clear\n```\n## Installation\nRecommended installation with [`pipx`](https://github.com/pypa/pipx):\n```shell\npipx install kvsh\n```\nTab completion with [`argcomplete`](https://github.com/kislyuk/argcomplete):\n```shell\npipx install argcomplete\neval "$(register-python-argcomplete kv)"\neval "$(register-python-argcomplete kvv)"\n```',
    'author': 'Aatif Syed',
    'author_email': 'aatifsyedyp@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/aatifsyed/kvsh',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
