# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ast_monitor']

package_data = \
{'': ['*']}

install_requires = \
['PyQt5',
 'adafruit-circuitpython-gps',
 'geopy',
 'matplotlib',
 'pyqt-feedback-flow',
 'sport-activities-features',
 'tcxreader']

setup_kwargs = {
    'name': 'ast-monitor',
    'version': '0.1.1',
    'description': 'AST-Monitor is a wearable Raspberry Pi computer for cyclists',
    'long_description': '# AST-Monitor --- A wearable Raspberry Pi computer for cyclists\n\nThis repository is devoted to the AST-monitor, i.e. a low-cost and efficient embedded device for monitoring the realization of sport training sessions that is dedicated to monitor cycling training sessions.\nAST-Monitor is a part of Artificial Sport Trainer (AST) system. First bits of AST-monitor were presented in the following [paper](https://arxiv.org/abs/2109.13334).\n\n## Outline of this repository\n\nThis repository presents basic code regarded to GUI. It was ported from the initial prototype to poetry.\n\n## Hardware outline\n\nThe complete hardware part is shown in Fig from which it can be seen that the AST-computer is split into the following pieces:\n\n* a platform with fixing straps that attach to a bicycle,\n* the Raspberry Pi 4 Model B micro-controller with Raspbian OS installed,\n* a five-inch LCD touch screen display,\n* a USB ANT+ stick,\n* Adafruit\'s Ultimate GPS HAT module.\n\n<p align="center">\n  <img width="600" src="https://raw.githubusercontent.com/firefly-cpp/AST-Monitor/main/.github/img/complete_small.JPG" alt="AST-Monitor">\n</p>\n\n\nA Serial Peripheral Interface (SPI) protocol was dedicated for communication between the Raspberry Pi and the GPS peripheral. A specialized USB ANT+ stick was used to capture the HR signal. The screen display was connected using a modified (physically shortened) HDMI cable, while the touch feedback was implemented using physical wires. The computer was powered during the testing phase using the Trust\'s (5 VDC) power-bank. The AST-Monitor prototype is still a little bulky, but a more discrete solution is being searched for, including the sweat drainer of the AST.\n\n## Software outline\n\n### Dependencies\n\nList of dependencies:\n\n| Package      | Version    | Platform |\n| ------------ |:----------:|:--------:|\n| PyQt5        | ^5.15.6    | All      |\n| matplotlib   | ^3.5.1     | All      |\n| geopy        | ^2.2.0     | All      |\n| openant        | v0.4     | All      |\n| pyqt-feedback-flow       | ^0.1.0     | All      |\n| tcxreader       | ^0.3.8     | All      |\n| sport-activities-features       | ^0.2.9     | All      |\n\nNote: openant package should be installed manually. Please follow to the [official instructions](https://github.com/Tigge/openant). If you use Fedora OS, you can install openant package using dnf package manager:\n\n```sh\n$ dnf install python-openant\n```\n\n## Installation\n\nInstall AST-monitor with pip:\n\n```sh\n$ pip install ast-monitor\n```\nIn case you want to install directly from the source code, use:\n\n```sh\n$ git clone https://github.com/firefly-cpp/AST-Monitor.git\n$ cd AST-Monitor\n$ poetry build\n$ python setup.py install\n```\n\n## Deployment\n\nOur project was deployed on Raspberry Pi device using Raspbian OS.\n\n### Run AST-Monitor on startup\n\nAdd following lines in /etc/profile which ensures to run scripts on startup:\n\n```sh\nsudo python3 /home/user/run_example.py\nsudo nohup python3 /home/user/read_hr_data.py  &\nsudo nohup python3 /home/user/read_gps_data.py  &\n```\n## Examples\n\n### Basic run\n\n```python\nfrom PyQt5 import QtCore, QtGui, uic, QtWidgets\nfrom ast_monitor.model import AST\nimport sys\n\n# provide data locations\n\nhr_data = "sensor_data/hr.txt"\ngps_data = "sensor_data/gps.txt"\n\n\nif __name__ == "__main__":\n    app = QtWidgets.QApplication(sys.argv)\n    window = AST(hr_data, gps_data)\n\n    window.show()\n    sys.exit(app.exec_())\n```\n\n\n## License\n\nThis package is distributed under the MIT License. This license can be found online at <http://www.opensource.org/licenses/MIT>.\n\n## Disclaimer\n\nThis framework is provided as-is, and there are no guarantees that it fits your purposes or that it is bug-free. Use it at your own risk!\n\n## Reference\n\nFister Jr, I., Fister, I., Iglesias, A., Galvez, A., Deb, S., & Fister, D. (2021). On deploying the Artificial Sport Trainer into practice. arXiv preprint [arXiv:2109.13334](https://arxiv.org/abs/2109.13334).\n',
    'author': 'Iztok Fister Jr.',
    'author_email': 'iztok@iztok-jr-fister.eu',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
