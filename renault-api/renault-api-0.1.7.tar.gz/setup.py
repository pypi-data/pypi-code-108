# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['renault_api',
 'renault_api.cli',
 'renault_api.cli.charge',
 'renault_api.cli.hvac',
 'renault_api.gigya',
 'renault_api.kamereon']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.7.1,<4.0.0',
 'marshmallow-dataclass>=8.2.0,<9.0.0',
 'pyjwt>=1.7.1,<3.0.0']

extras_require = \
{'cli': ['click>=8.0.1,<9.0.0',
         'tabulate>=0.8.7,<0.9.0',
         'dateparser>=1.0.0,<2.0.0']}

entry_points = \
{'console_scripts': ['renault-api = renault_api.cli.__main__:main']}

setup_kwargs = {
    'name': 'renault-api',
    'version': '0.1.7',
    'description': 'Renault API',
    'long_description': 'Renault API\n===========\n\n|PyPI| |Python Version| |License|\n\n|Read the Docs| |Tests| |Codecov|\n\n|pre-commit| |Black|\n\n.. |PyPI| image:: https://img.shields.io/pypi/v/renault-api.svg\n   :target: https://pypi.org/project/renault-api/\n   :alt: PyPI\n.. |Python Version| image:: https://img.shields.io/pypi/pyversions/renault-api\n   :target: https://pypi.org/project/renault-api\n   :alt: Python Version\n.. |License| image:: https://img.shields.io/pypi/l/renault-api\n   :target: https://opensource.org/licenses/MIT\n   :alt: License\n.. |Read the Docs| image:: https://img.shields.io/readthedocs/renault-api/latest.svg?label=Read%20the%20Docs\n   :target: https://renault-api.readthedocs.io/\n   :alt: Read the documentation at https://renault-api.readthedocs.io/\n.. |Tests| image:: https://github.com/hacf-fr/renault-api/workflows/Tests/badge.svg\n   :target: https://github.com/hacf-fr/renault-api/actions?workflow=Tests\n   :alt: Tests\n.. |Codecov| image:: https://codecov.io/gh/hacf-fr/renault-api/branch/main/graph/badge.svg\n   :target: https://codecov.io/gh/hacf-fr/renault-api\n   :alt: Codecov\n.. |pre-commit| image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white\n   :target: https://github.com/pre-commit/pre-commit\n   :alt: pre-commit\n.. |Black| image:: https://img.shields.io/badge/code%20style-black-000000.svg\n   :target: https://github.com/psf/black\n   :alt: Black\n\n\nFeatures\n--------\n\nThis Python package manages the communication with the private Renault API used by the official MyRenault application.\n\nThe client is able to read various vehicle attributes, such as:\n\n* mileage\n* GPS location\n* fuel autonomy (for fuel vehicles)\n* battery autonomy (for electric vehicles)\n* contracts associated to the vehicle (warranty and connected services)\n\nFor some vehicles, it is also possible to manage:\n\n* hvac/pre-conditionning of the vehicle\n* charge schedule\n\nThis package has been developed to be used with Home-Assistant, but it can be used in other contexts\n\n\nRequirements\n------------\n\n* Python (>= 3.7.1)\n\nAPI Usage\n---------\n\nYou can install *Renault API* via pip_ from PyPI_:\n\n.. code:: console\n\n   $ pip install renault-api\n\n.. code:: python\n\n   import aiohttp\n   import asyncio\n\n   from renault_api.renault_client import RenaultClient\n\n   async def main():\n      async with aiohttp.ClientSession() as websession:\n         client = RenaultClient(websession=websession, locale="fr_FR")\n         await client.session.login(\'email\', \'password\')\n         print(f"Accounts: {await client.get_person()}") # List available accounts, make a note of kamereon account id\n\n         account_id = "Your Kamereon account id"\n         account = await client.get_api_account(account_id)\n         print(f"Vehicles: {await account.get_vehicles()}") # List available vehicles, make a note of vehicle VIN\n\n         vin = "Your vehicle VIN"\n         vehicle = await account.get_api_vehicle(vin)\n         print(f"Cockpit information: {await vehicle.get_cockpit()}")\n         print(f"Battery status information: {await vehicle.get_battery_status()}")\n\n   loop = asyncio.get_event_loop()\n   loop.run_until_complete(main())\n\nCLI Usage\n---------\n\nThe renault-api is also available through a CLI, which requires additional dependencies.\nFor the added dependencies, you can install *Renault API* via pip_ from PyPI_:\n\n.. code:: console\n\n   $ pip install renault-api[cli]\n\nOnce installed, the following command prompts for credentials and settings, displays basic vehicle status information, and generates traces:\n\n.. code:: console\n\n   $ renault-api --log status\n\n* Credentials will automatically be stored in the user home directory (~/.credentials/renault-api.json)\n* Logs will automatically be generated in `logs` subfolder\n\nPlease see the `Command-line Reference <Usage_>`_ for full details.\n\n\nContributing\n------------\n\nContributions are very welcome.\nTo learn more, see the `Contributor Guide`_.\n\n\nLicense\n-------\n\nDistributed under the terms of the MIT_ license,\n*Renault API* is free and open source software.\n\n\nDisclaimer\n----------\n\nThis project is not affiliated with, endorsed by, or connected to Renault. I accept no responsibility for any consequences, intended or accidental, as a as a result of interacting with Renault\'s API using this project.\n\n\nIssues\n------\n\nIf you encounter any problems,\nplease `file an issue`_ along with a detailed description.\n\n\nCredits\n-------\n\nThis project was generated from `@cjolowicz`_\'s `Hypermodern Python Cookiecutter`_ template.\nThis project was heavily based on `@jamesremuscat`_\'s `PyZE`_ python client for the Renault ZE API.\n\n\n.. _@cjolowicz: https://github.com/cjolowicz\n.. _Cookiecutter: https://github.com/audreyr/cookiecutter\n.. _@jamesremuscat: https://github.com/jamesremuscat\n.. _PyZE: https://github.com/jamesremuscat/pyze\n.. _MIT: http://opensource.org/licenses/MIT\n.. _PyPI: https://pypi.org/\n.. _Hypermodern Python Cookiecutter: https://github.com/cjolowicz/cookiecutter-hypermodern-python\n.. _file an issue: https://github.com/hacf-fr/renault-api/issues\n.. _pip: https://pip.pypa.io/\n.. github-only\n.. _Contributor Guide: CONTRIBUTING.rst\n.. _Usage: https://renault-api.readthedocs.io/en/latest/usage.html\n',
    'author': 'epenet',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/hacf-fr/renault-api',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7.1,<4.0.0',
}


setup(**setup_kwargs)
