# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['zm_au']

package_data = \
{'': ['*']}

install_requires = \
['packaging>=20.9,<21.0', 'zetuptools>=4.0.0,<5.0.0', 'zmtools>=2.0.0,<3.0.0']

setup_kwargs = {
    'name': 'zm-au',
    'version': '1.1.1',
    'description': 'Auto-updater for programs',
    'long_description': '# `zm-au`\n\n`zm-au` is a developer tool that provides an auto-updating API for programs. Note that this can be a bad idea for many reasons, so you should probably ask the user first.\n\nSorry for prefixing the name with "zm", but I\'m sure I\'ll have to do that again as I have no creative names for anything anymore.\n\n## Usage\n\n`zm-au` comes with two useful auto-updaters, `PipAU` and `PipGitHubAU`, and a class to base an auto-updater off of.\n\nLet\'s say you are creating a Python package called `skippitybop` and you want it to notify the user when there is an update available on PyPI for it. Simply insert this code where you want the update check to happen.\n\n```python\nfrom zm_au import PipAU\n\nupdater = PipAU("skippitybop")\nupdater.update(prompt=True)\n```\n\nWhen the code is run, if there is an update available on PyPI, the user will be prompted to install it via `pip`. If the user chooses to install it, the program will exit on success. Or failure, for that matter.\n\nTake a guess what `prompt=False` would do.\n\nLet\'s say you are creating a Python package called `boppityskip` on bigboi\'s GitHub repo and you want it to notify the user when there is an update available on GitHub releases for it, probably because the package is private and not on PyPI. Insert this code where you want the update check to happen.\n\n```python\nfrom zm_au import PipGitHubAU\n\nupdater = PipGitHubAU("boppityskip", "bigboi/boppityskip", check_prerelease=True, dist="whl")\nupdater.update(prompt=True)\n```\n\nWhen the code is run, if there is an update available on GitHub releases (including prereleases) that is a `whl` file, the user will be prompted to install it via `pip`. Again, if the user chooses to install it, the program will exit on success or failure.\n\nYou can build your own AUs by making a class that inherits from `BaseAU`. Override the following functions as such.\n\n- `_get_current_version` - Must return the current version of the package\n- `_get_latest_version` - Must return the latest version of the package\n- `_download` - Must download the package and return the filename of the downloaded file\n- `_update` - Must install a package whose location is passed via the only parameter of this function\n\nBe smart about how you use this!\n',
    'author': 'Zeke Marffy',
    'author_email': 'zmarffy@yahoo.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/zmarffy/au',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
