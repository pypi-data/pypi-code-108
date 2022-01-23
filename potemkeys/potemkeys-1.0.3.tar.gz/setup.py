# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['potemkeys', 'potemkeys.tests']

package_data = \
{'': ['*']}

install_requires = \
['json5>=0.9.6,<0.10.0',
 'mergedeep>=1.3.4,<2.0.0',
 'pygame>=2.1.2,<3.0.0',
 'pynput>=1.7.6,<2.0.0']

extras_require = \
{':sys_platform != "win32"': ['python3-xlib'],
 ':sys_platform == "win32"': ['pywin32-ctypes']}

setup_kwargs = {
    'name': 'potemkeys',
    'version': '1.0.3',
    'description': 'Fighting games for goldfish with keyboards >:3c',
    'long_description': '# Potemkeys: Previously "FGfGwK: Fighting Games for Goldfish with Keyboards"\n\n## TL;DR Download!\n\n### [Windows, click here.](https://github.com/HenryFBP/potemkeys/releases/download/latest-windows/potemkeys.exe)\n\n### [Linux, click here.](https://github.com/HenryFBP/potemkeys/releases/download/latest-ubuntu/potemkeys) (must run `sudo apt-get install -y xdotool wmctrl`!)\n\n### Old name was FGfGwK\n\nThis used to be called "FGfGwK", "Fighting games for Goldfish with Keyboards" (Can\'t remember button maps).\n\nCredit to @flexadecimal for the new name, "potemkeys" (Potemkin from Guilty Gear + "keys")\n\n### PyPI\n\n-   <https://pypi.org/project/potemkeys/>\n\n### Using pip\n\n    pip install --upgrade potemkeys\n    python -m potemkeys\n\n[![forthebadge](https://forthebadge.com/images/badges/you-didnt-ask-for-this.svg)](https://forthebadge.com)\n\n[![forthebadge](https://forthebadge.com/images/badges/built-with-swag.svg)](https://forthebadge.com)\n\n[![forthebadge](https://forthebadge.com/images/badges/check-it-out.svg)](https://forthebadge.com)\n\n[![forthebadge](https://forthebadge.com/images/badges/compatibility-club-penguin.svg)](https://forthebadge.com)\n\n![A picture of the application.](/media/screenshot1.png)\n\n![Another picture of the application.](/media/screenshot2.png)\n\n## What is this?\n\nFor those who can\'t remember {keyboard input => controller} mappings, and want to see them in-game.\n\nCreated because TEKKEN doesn\'t show input conversions in multiplayer matches, and neither does Guilty Gear: Strive, \nand I wanted to see my inputs, so I wasted 6 hours writing this tool.\n\nWorks on Windows 11, and tested on Ubuntu.\n\n## This tool sucks, it doesn\'t do X!\n\nSee [./TODO.md](./TODO.md). Or fork this repo and add it yourself, and make a Pull Request, I\'ll probably accept your changes.\n\n## How do I use it?\n\nSee <https://github.com/HenryFBP/potemkeys/releases> and download the provided exe/binary file.\n \nIf you put `potemkeysoptions.jsonc` in the same folder as the EXE file, it will prefer that over its temporary directory.\n\nIf you want to know where the temp file is, look at the console output when the .exe first starts up.\n\n##  Development\n\n1.  Install Python version 3.whatever\n2.  Clone this repo\n3.  In the repo\'s folder, run:\n\n    ```\n    ./scripts/setup[.cmd|.sh]\n    ./scripts/start[.cmd|.sh]\n    ```\n\n4.  The window should stay on top.\n\n    ***Play your game in borderless/windowed mode*** and see the inputs get transformed and shown to you.\n\n### Build WHL\n\n    poetry build\n\n#### Test built WHL\n\n    pip install .\\dist\\potemkeys-whatever-version-1.2.3.4.5-py3-none-any.whl --force-reinstall\n\n### Deploy to PyPI\n\n    poetry publish --build\n\n### Testing exe generation\n\n    ./scripts/generate_exe[.cmd|.sh]\n    ./dist/potemkeys[.exe|.app]\n\n## Config\n\nEdit [`potemkeysoptions.jsonc`](/potemkeys/potemkeysoptions.jsonc).\n\nYou can make keymaps for literally any game that uses keyboard, by cloning the items under `keymaps`.\n\nIf you make one and want to see it included in the "official" branch of this tool, just fork this repo and make a PR.\n\n## License\n\nNo license, DWYW, I\'m not your dad.\n\nJust make sure to link/PR, or just fork it if I die or something :P\n\n## VIRUSES????\n\nhttps://www.reddit.com/r/learnpython/comments/e99bhe/why_does_pyinstaller_trigger_windows_defender\n\n### REEEEEEEEEEEEEEE\n\nhttps://docs.microsoft.com/en-us/previous-versions/windows/internet-explorer/ie-developer/platform-apis/ms537361(v=vs.85)?redirectedfrom=MSDN\n',
    'author': 'henryfbp',
    'author_email': 'HenryFBP@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/henryfbp/potemkeys',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
