# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['givenergy_modbus', 'givenergy_modbus.model', 'tests', 'tests.model']

package_data = \
{'': ['*']}

install_requires = \
['click==8.0.1',
 'crccheck>=1.1,<2.0',
 'loguru>=0.5.3,<0.6.0',
 'pydantic>=1.8.2,<2.0.0',
 'pymodbus>=2.5.3,<3.0.0']

extras_require = \
{'dev': ['tox>=3.20.1,<4.0.0',
         'virtualenv>=20.2.2,<21.0.0',
         'pip>=20.3.1,<21.0.0',
         'twine>=3.3.0,<4.0.0',
         'toml>=0.10.2,<0.11.0',
         'bump2version>=1.0.1,<2.0.0'],
 'doc': ['mkdocs>=1.1.2,<2.0.0',
         'mkdocs-include-markdown-plugin>=1.0.0,<2.0.0',
         'mkdocs-material>=6.1.7,<7.0.0',
         'mkdocstrings>=0.15.2,<0.16.0',
         'mkdocs-autorefs>=0.2.1,<0.3.0'],
 'test': ['black>=21.5b2,<22.0',
          'isort>=5.8.0,<6.0.0',
          'flake8>=4.0.0,<5.0.0',
          'flake8-docstrings>=1.6.0,<2.0.0',
          'mypy>=0.900,<0.901',
          'pytest>=6.2.4,<7.0.0',
          'pytest-cov>=2.12.0,<3.0.0']}

entry_points = \
{'console_scripts': ['givenergy-modbus = givenergy_modbus.cli:main']}

setup_kwargs = {
    'name': 'givenergy-modbus',
    'version': '0.9.2',
    'description': 'A python library to access GivEnergy inverters via Modbus TCP, with no dependency on the GivEnergy Cloud.',
    'long_description': '# GivEnergy Modbus\n\n[![pypi](https://img.shields.io/pypi/v/givenergy-modbus.svg)](https://pypi.org/project/givenergy-modbus/)\n[![python](https://img.shields.io/pypi/pyversions/givenergy-modbus.svg)](https://pypi.org/project/givenergy-modbus/)\n[![Build Status](https://github.com/dewet22/givenergy-modbus/actions/workflows/dev.yml/badge.svg)](https://github.com/dewet22/givenergy-modbus/actions/workflows/dev.yml)\n[![codecov](https://codecov.io/gh/dewet22/givenergy-modbus/branch/main/graphs/badge.svg)](https://codecov.io/github/dewet22/givenergy-modbus)\n\nA python library to access GivEnergy inverters via Modbus TCP on a local network, with no dependency on the GivEnergy\nCloud. This extends [pymodbus](https://pymodbus.readthedocs.io/) by providing a custom framer, decoder and PDUs that are\nspecific to the GivEnergy implementation.\n\n> ⚠️ This project makes no representations as to its completeness or correctness. You use it at your own risk — if your\n> inverter mysteriously explodes because you accidentally set the `BOOMTIME` register or you consume a MWh of\n> electricity doing SOC calibration: you **really** are on your own. We make every effort to prevent you from shooting\n> yourself in the foot, so as long as you use the client and its exposed methods, you should be perfectly safe.\n\n* Documentation: <https://dewet22.github.io/givenergy-modbus>\n* GitHub: <https://github.com/dewet22/givenergy-modbus>\n* PyPI: <https://pypi.org/project/givenergy-modbus/>\n* Free software: Apache-2.0\n\n## Features\n\n* Reading all registers and decoding them into their representative datatypes\n* Writing data to holding registers that are deemed to be safe to set configuration on the inverter\n\n## How to use\n\nUse the provided client to interact with the device over the network, and register caches to build combined state of a\ndevice:\n\n```python\nimport datetime\nfrom givenergy_modbus.client import GivEnergyClient\nfrom givenergy_modbus.model.battery import Battery\nfrom givenergy_modbus.model.inverter import Inverter, Model\nfrom givenergy_modbus.model.register_cache import RegisterCache\n\nclient = GivEnergyClient(host="192.168.99.99")\n\n# change configuration on the device:\nclient.enable_charge_target(80)\n# set a charging slot from 00:30 to 04:30\nclient.set_charge_slot_1((datetime.time(hour=0, minute=30), datetime.time(hour=4, minute=30)))\n# set the inverter to charge when there\'s excess, and discharge otherwise. it will also respect charging slots.\nclient.set_mode_dynamic()\n\nrc = RegisterCache()\nclient.update_inverter_registers(rc)\ninverter = Inverter.from_orm(rc)\nassert inverter.inverter_serial_number == \'SA1234G567\'\nassert inverter.inverter_model == Model.Hybrid\nassert inverter.v_pv1 == 1.4  # V\nassert inverter.e_battery_discharge_day == 8.1  # kWh\nassert inverter.enable_charge_target\nassert inverter.dict() == {\n    \'inverter_serial_number\': \'SA1234G567\',\n    \'device_type_code\': \'3001\',\n    \'charge_slot_1\': (datetime.time(0, 30), datetime.time(7, 30)),\n    \'f_ac1\': 49.98,\n    ...\n}\nassert inverter.json() == \'{"inverter_serial_number": "SA1234G567", "device_type_code": "3001", ...\'\n\n# it is _probably_ a good idea to not share register caches across devices\nrc = RegisterCache()\nclient.update_battery_registers(rc, battery_number=0)\nbattery = Battery.from_orm(rc)\n\nassert battery.serial_number == \'BG1234G567\'\nassert battery.v_battery_cell_01 == 3.117\nassert battery.dict() == {\n    \'bms_firmware_version\': 3005,\n    \'design_capacity\': 160.0,\n    ...\n}\nassert battery.json() == \'{"battery_serial_number": "BG1234G567", "v_battery_cell_01": 3.117, ...\'\n```\n\n## Credits\n\nThis package was created with [Cookiecutter](https://github.com/audreyr/cookiecutter) and\nthe [waynerv/cookiecutter-pypackage](https://github.com/waynerv/cookiecutter-pypackage) project template.\n',
    'author': 'Dewet Diener',
    'author_email': 'givenergy-modbus@dewet.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/dewet22/givenergy-modbus',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
