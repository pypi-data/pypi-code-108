# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pepe_qrcode_cli']

package_data = \
{'': ['*']}

install_requires = \
['Pillow>=9.0.0,<10.0.0',
 'pyzbar>=0.1.8,<0.2.0',
 'qrcode>=7.3.1,<8.0.0',
 'typer[all]>=0.4.0,<0.5.0']

entry_points = \
{'console_scripts': ['pepe-qrcode-cli = pepe_qrcode_cli.main:app']}

setup_kwargs = {
    'name': 'pepe-qrcode-cli',
    'version': '0.4.0',
    'description': 'QRCode CLI for generating simple QR codes',
    'long_description': '# School Project\n\nAwesome QRCode Command-line interface',
    'author': 'Pepe',
    'author_email': 'pimanroya06@gmail.com',
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
