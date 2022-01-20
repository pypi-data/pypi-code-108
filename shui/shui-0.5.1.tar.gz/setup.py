# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['shui', 'shui.classes', 'shui.commands', 'shui.functions']

package_data = \
{'': ['*']}

install_requires = \
['beautifulsoup4>=4.8.0,<5.0.0',
 'cleo>=0.7.0,<0.8.0',
 'packaging>=21.0,<22.0',
 'pathlib3x>=1.3.6,<2.0.0',
 'requests>=2.25.0,<3.0.0',
 'tqdm>=4.60.0,<5.0.0',
 'url-normalize>=1.4.0,<2.0.0',
 'urllib3>=1.25.2,<2.0.0']

entry_points = \
{'console_scripts': ['shui = shui.cli:main']}

setup_kwargs = {
    'name': 'shui',
    'version': '0.5.1',
    'description': 'Spark-Hadoop Unix Installer',
    'long_description': '# SHUI\nSpark-Hadoop Unix Installer\n\n![OSes](https://img.shields.io/badge/system-macOS%7CLinux%7CFreeBSD-green)\n![Architectures](https://img.shields.io/badge/arch-i686%7Cx86__64-yellowgreen)\n\n[![Python](https://img.shields.io/pypi/pyversions/shui.svg?logo=python&logoColor=white)](https://pypi.org/project/shui)\n[![PyPI version](https://badge.fury.io/py/shui.svg)](https://badge.fury.io/py/shui)\n[![PyPI downloads](https://img.shields.io/pypi/dm/shui)](https://img.shields.io/pypi/dm/shui)\n[![Code style](https://github.com/jemrobinson/shui/workflows/check-code-style/badge.svg)](https://github.com/jemrobinson/shui/actions)\n[![Functionality](https://github.com/jemrobinson/shui/workflows/test-functionality/badge.svg)](https://github.com/jemrobinson/shui/actions)\n\nThis package uses Python to download and unpack a pre-built version of Spark/Hadoop from Apache.\nIts primary use-case is simplifying unattended installs where the user wants "the latest available version" of these tools.\n\n## Features\n\n- download Spark/Hadoop release tarball from Apache.\n- verify the tarball using the SHA512 sum provided by Apache.\n- unpack the tarball to a target directory on your local system.\n\n## Installation\n\nFirst you\'ll need to install `shui` using pip: `pip install shui`.\n\n## Usage\n\n### Versions\nThe `versions` command shows you all available Spark/Hadoop versions.\n\n```\nUSAGE\n  shui versions [--latest]\n\nOPTIONS\n  --latest               Show only the latest available version\n\nGLOBAL OPTIONS\n  -h (--help)            Display this help message\n  -q (--quiet)           Do not output any message\n  -v (--verbose)         Increase the verbosity of messages: "-v" for normal output, "-vv" for more verbose output and "-vvv" for debug\n  -V (--version)         Display this application version\n  --ansi                 Force ANSI output\n  --no-ansi              Disable ANSI output\n  -n (--no-interaction)  Do not ask any interactive question\n```\n\n### Install\nThe `install` command will download, verify and install a particular Spark/Hadoop version.\n\n```\nUSAGE\n  shui install [--latest] [--spark\xa0<...>] [--hadoop\xa0<...>] [--target\xa0<...>]\n\nOPTIONS\n  --latest               Use the latest available version\n  --spark                Spark version (default: "any")\n  --hadoop               Hadoop version (default: "any")\n  --target               Directory to install into (default: "cwd")\n\nGLOBAL OPTIONS\n  -h (--help)            Display this help message\n  -q (--quiet)           Do not output any message\n  -v (--verbose)         Increase the verbosity of messages: "-v" for normal output, "-vv" for more verbose output and "-vvv" for debug\n  -V (--version)         Display this application version\n  --ansi                 Force ANSI output\n  --no-ansi              Disable ANSI output\n  -n (--no-interaction)  Do not ask any interactive question\n```\n',
    'author': 'James Robinson',
    'author_email': 'james.em.robinson@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/jemrobinson/shui',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
