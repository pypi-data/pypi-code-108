# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['blueye', 'blueye.sdk']

package_data = \
{'': ['*']}

install_requires = \
['blueye.protocol>=1.3.4,<2.0.0',
 'numpy>=1.21.5,<1.22.0',
 'packaging>=20.1,<21.0',
 'requests>=2.22.0,<3.0.0',
 'tabulate>=0.8.5,<0.9.0']

extras_require = \
{'examples': ['asciimatics>=1.11.0,<2.0.0',
              'inputs>=0.5,<0.6',
              'pandas>=1.3,<2.0',
              'matplotlib>=3.1.1,<4.0.0',
              'webdavclient3>=3.14.6,<4.0.0']}

setup_kwargs = {
    'name': 'blueye.sdk',
    'version': '1.0.0',
    'description': 'SDK for controlling a Blueye underwater drone',
    'long_description': '# blueye.sdk\n[![Tests](https://github.com/BluEye-Robotics/blueye.sdk/workflows/Tests/badge.svg)](https://github.com/BluEye-Robotics/blueye.sdk/actions)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)\n[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/BluEye-Robotics/blueye.sdk.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/BluEye-Robotics/blueye.sdk/context:python)\n[![codecov](https://codecov.io/gh/BluEye-Robotics/blueye.sdk/branch/master/graph/badge.svg)](https://codecov.io/gh/BluEye-Robotics/blueye.sdk)\n[![PyPi-version](https://img.shields.io/pypi/v/blueye.sdk.svg?maxAge=3600)](https://pypi.org/project/blueye.sdk/)\n[![python-versions](https://img.shields.io/pypi/pyversions/blueye.sdk.svg?longCache=True)](https://pypi.org/project/blueye.sdk/)\n_________________\n\n[Read Latest Documentation](https://blueye-robotics.github.io/blueye.sdk/) - [Browse GitHub Code Repository](https://github.com/BluEye-Robotics/blueye.sdk)\n_________________\n\nA Python package for remote control of the Blueye underwater drones.\n\n\n![SDK demo](https://user-images.githubusercontent.com/8504604/66751230-d05c7e00-ee8e-11e9-91cb-d46b433aafa5.gif)\n\n## About Blueye Underwater Drones\nBlueye produces and sells three models of underwater drones, the Blueye Pioneer, Blueye Pro, and Blueye X3. The Pioneer and the Pro are drones designed for inspection, while the X3 is extensible with three guest ports that allow attaching for example grippers or sonars.\nVisit [blueyerobotics.com](https://www.blueyerobotics.com/products) for more information about the Blueye products.\n\n## This SDK and the Blueye drones\nA Blueye drone is normally controlled via a mobile device through the Blueye App ([iOS](https://apps.apple.com/no/app/blueye/id1369714041)/[Android](https://play.google.com/store/apps/details?id=no.blueye.blueyeapp)).\nThe mobile device is connected via Wi-Fi to a surface unit, and the drone is connected to the surface unit via a tether cable.\n\nThis python SDK exposes the functionality of the Blueye app through a Python object. The SDK enables remote control of a Blueye drone as well as reading telemetry data and viewing video streams. It is not meant for executing code on the drone itself.\n\nTo control the drone you connect your laptop to the surface unit Wi-Fi and run code that interfaces with the through the Python object.\n\n\nCheck out the [`Quick Start Guide`](https://blueye-robotics.github.io/blueye.sdk/docs/quick_start/) to get started with using the SDK.\n',
    'author': 'Sindre Hansen',
    'author_email': 'sindre.hansen@blueye.no',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://www.blueyerobotics.com',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7.1,<3.11',
}


setup(**setup_kwargs)
