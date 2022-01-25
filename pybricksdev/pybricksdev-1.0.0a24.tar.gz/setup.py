# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pybricksdev',
 'pybricksdev.ble',
 'pybricksdev.ble.lwp3',
 'pybricksdev.cli',
 'pybricksdev.cli.lwp3',
 'pybricksdev.resources',
 'pybricksdev.tools']

package_data = \
{'': ['*']}

install_requires = \
['aioserial>=1.3.0,<2.0.0',
 'appdirs>=1.4.4,<2.0.0',
 'argcomplete>=1.11.1,<2.0.0',
 'asyncssh>=2.2.1,<3.0.0',
 'bleak>=0.14.1,<0.15.0',
 'mpy-cross==1.14',
 'prompt-toolkit>=3.0.18,<4.0.0',
 'pyusb>=1.0.2,<2.0.0',
 'semver>=2.13.0,<3.0.0',
 'tqdm>=4.62.3,<5.0.0',
 'validators>=0.18.2,<0.19.0']

entry_points = \
{'console_scripts': ['pybricksdev = pybricksdev.cli:main']}

setup_kwargs = {
    'name': 'pybricksdev',
    'version': '1.0.0a24',
    'description': 'Pybricks developer tools',
    'long_description': '[![Coverage Status](https://coveralls.io/repos/github/pybricks/pybricksdev/badge.svg?branch=master)](https://coveralls.io/github/pybricks/pybricksdev?branch=master) [![Documentation Status](https://readthedocs.org/projects/pybricksdev/badge/?version=latest)](https://docs.pybricks.com/projects/pybricksdev/en/latest/?badge=latest)\n\n# Pybricks tools & interface library\n\nThis is a package with tools for Pybricks developers. For regular users we\nrecommend the [Pybricks Code][code] web IDE.\n\nThis package contains both command line tools and a library to call equivalent\noperations from within a Python script.\n\n[code]: https://www.code.pybricks.com\n\n## Installation\n\n### Python Runtime\n\n`pybricksdev` requires Python 3.8 or higher.\n\n- For Windows, use the [official Python installer][py-dl] or the [Windows Store][py38-win].\n- For Mac, use the [official Python installer][py-dl] or Homebrew (`brew install python@3.8`).\n- For Linux, use the distro provided `python3.8` or if not available, use a Python\n  runtime version manager such as [asdf][asdf] or [pyenv][pyenv].\n\n\n[py-dl]: https://www.python.org/downloads/\n[py38-win]: https://www.microsoft.com/en-us/p/python-38/9mssztt1n39l\n[asdf]: https://asdf-vm.com\n[pyenv]: https://github.com/pyenv/pyenv\n\n### Command Line Tool\n\nWe recommend using [pipx] to install `pybricksdev` as a command line tool.\n\nWe also highly recommend installing `pipx` using a package manager such as `apt`,\n`brew`, etc. as suggested in the official [pipx installation] instructions.\n\nAnd don\'t forget to run `pipx ensurepath` after the initial installation.\nThis will make it so that tools installed with `pipx` are in your `PATH`.\nYou will need to restart any terminal windows for this to take effect. If that\ndoesn\'t work, try logging out and logging back in.\n\nThen use `pipx` to install `pybricksdev`:\n\n    # POSIX shell (Linux, macOS, Cygwin, etc)\n    PIPX_DEFAULT_PYTHON=python3.8 pipx install pybricksdev\n\nSetting the `PIPX_DEFAULT_PYTHON` environment variable is only needed when\n`pipx` uses a different Python runtime other that Python 3.8. This may be the\ncase if your package manager uses a different Python runtime.\n\n[pipx]: https://pipxproject.github.io/pipx/\n[pipx installation]: https://pipxproject.github.io/pipx/installation/\n\n#### Windows users\n\nIf you are using the *Python Launcher for Windows* (installed by default with\nthe official Python installer), then you will need to use `py -3.8` instead\nof `python3.8`.\n\n    py -3.8 -m pip install --upgrade pip # ensure pip is up to date first\n    py -3.8 -m pip install pipx\n    py -3.8 -m pipx ensurepath\n    py -3.8 -m pipx install pybricksdev\n\n#### Linux USB\n\nOn Linux, `udev` rules are needed to allow access via USB. The `pybricksdev`\ncommand line tool contains a function to generate the required rules. Run the\nfollowing:\n\n    pybricksdev udev | sudo tee /etc/udev/rules.d/99-pybricksdev.rules\n\n### Library\n\nTo install `pybricksdev` as a library, we highly recommend using a virtual\nenvironment for your project. Our tool of choice for this is [poetry][poetry]:\n\n    poetry env use python3.8\n    poetry add pybricksdev\n\nOf course you can always use `pip` as well:\n\n    pip install pybricksdev --pre\n\n\n[poetry]: https://python-poetry.org\n\n\n## Using the Command Line Tool\n\nThe following are some examples of how to use the `pybricksdev` command line tool.\nFor additional info, run `pybricksdev --help`.\n\n### Flashing Pybricks MicroPython firmware\n\nMake sure the hub is off. Press and keep holding the hub button, and run:\n\n    pybricksdev flash <firmware.zip>\n\nReplace `<firmware.zip>` with the actual path to the firmware archive.\n\nYou may release the button once the progress bar first appears. \n\nThe SPIKE Prime Hub and MINDSTORMS Robot Inventor Hub do not have a Bluetooth\nbootloader. It is recommended to [install Pybricks using a Python script][issue-167] that\nruns on the hub. You can also flash the firmware manually using [DFU](dfu).\n\n\n[dfu]: ./README_dfu.rst\n[issue-167]: https://github.com/pybricks/support/issues/167\n\n\n### Running Pybricks MicroPython programs\n\nThis compiles a MicroPython script and sends it to a hub with Pybricks\nfirmware.\n\n    pybricksdev run --help\n\n    #\n    # ble connection examples:\n    #\n    \n    # Run script on any Pybricks device\n    pybricksdev run ble demo/shortdemo.py\n\n    # Run script on the first device we find called Pybricks hub\n    pybricksdev run ble --name "Pybricks Hub" demo/shortdemo.py\n\n    # Run script on device with address 90:84:2B:4A:2B:75 (doesn\'t work on Mac)\n    pybricksdev run ble --name 90:84:2B:4A:2B:75 demo/shortdemo.py\n           \n    #\n    # usb connection examples:\n    # NOTE: running programs via usb connection works for official LEGO firmwares only\n\n    # Run script on any Pybricks device\n    pybricksdev run usb demo/shortdemo.py\n\n    #\n    # Other connection examples:\n    #\n\n    # Run script on ev3dev at 192.168.0.102\n    pybricksdev run ssh --name 192.168.0.102 demo/shortdemo.py\n\n\n### Compiling Pybricks MicroPython programs without running\n\nThis can be used to compile programs. Instead of also running them as above,\nit just prints the output on the screen instead.\n\n    pybricksdev compile demo/shortdemo.py\n\n    pybricksdev compile "print(\'Hello!\'); print(\'world!\');"\n\n\nThis is mainly intended for developers who want to quickly inspect the\ncontents of the `.mpy` file. To get the actual file, just use `mpy-cross`\ndirectly. We have used this tool in the past to test bare minimum MicroPython\nports that have neither a builtin compiler or any form of I/O yet. You can\npaste the generated `const uint8_t script[]` directly ito your C code.\n\n## Additional Documentation\n\nhttps://docs.pybricks.com/projects/pybricksdev (work in progress)\n',
    'author': 'The Pybricks Authors',
    'author_email': 'dev@pybricks.com',
    'maintainer': 'Laurens Valk',
    'maintainer_email': 'laurens@pybricks.com',
    'url': 'https://pybricks.com',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
