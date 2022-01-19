# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['boostedblob']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.7.2,<4.0.0',
 'pycryptodomex>=3.9,<4.0',
 'uvloop>=0.16.0,<0.17.0',
 'xmltodict>=0.12,<0.13']

entry_points = \
{'console_scripts': ['bbb = boostedblob.__main__:main']}

setup_kwargs = {
    'name': 'boostedblob',
    'version': '0.9.3',
    'description': 'Command line tool and async library to perform basic file operations on local paths, Google Cloud Storage paths and Azure Blob Storage paths.',
    'long_description': '# boostedblob\n\nboostedblob is a command line tool and async library to perform basic file operations on local\npaths, Google Cloud Storage paths and Azure Blob Storage paths.\n\nboostedblob is derived from the excellent [blobfile](https://github.com/christopher-hesse/blobfile).\n\nThe fun part of implementing boostedblob is `boostedblob/boost.py`, which provides a\n`concurrent.futures`-like interface for running and composing async tasks in a concurrency limited\nenvironment.\n\n## Installation\n\nJust run `pip install boostedblob`. boostedblob requires Python 3.7 or better.\n\n## Usage\n\nFor an overview and list of commands:\n```sh\nbbb --help\n```\n\nFor help with a specific command:\n```sh\nbbb ls --help\n```\n\nTo enable tab completion, add the following to your shell config (replacing `zsh` with `bash`, if appropriate):\n```sh\neval "$(bbb complete init zsh)"\n```\nNote that the quotes are necessary. You can also inline the result of `bbb complete init zsh` into\nyour shell config to make your shell startup a little faster.\n\n## Contributing\n\nTo get started with developing boostedblob and running tests, see [CONTRIBUTING.md](CONTRIBUTING.md)\n',
    'author': 'Shantanu Jain',
    'author_email': 'hauntsaninja@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
