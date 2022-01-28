# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['hikconnect']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.7.4,<4.0.0']

setup_kwargs = {
    'name': 'hikconnect',
    'version': '1.0.0',
    'description': 'Communicate with Hikvision smart doorbells via Hik-Connect cloud.',
    'long_description': '# Usage\n\n```python\nfrom hikconnect.api import HikConnect\n\nasync with HikConnect() as api:\n\n    await api.login("foo", "bar")\n\n    devices = [device async for device in api.get_devices()]\n    print(devices)\n    # [{\n    #   \'id\': \'DS-XXXXXX-YYYYYYYYYYYYYYYYYYYYYYYYY\',\n    #   \'name\': \'DS-XXXXXX-Y(ZZZZZZZZZ)\',\n    #   \'serial\': \'ZZZZZZZZZ\',\n    #   \'type\': \'DS-XXXXXX-Y\',\n    #   \'version\': \'V1.2.3 build 123456\',\n    #   \'locks\': {1: 2, 2: 0, 3: 1}\n    # }]\n    # locks data means (guessing): <channel number>: <number of locks connected>\n\n    my_device_serial = devices[0]["serial"]\n\n    cameras = [camera async for camera in api.get_cameras(my_device_serial)]\n    print(cameras)\n    # [\n    #   {\'id\': \'4203fd7c5f89ce96f8ff0adfdbe8b731\', \'name\': \'foo\', \'channel_number\': 1, \'signal_status\': 1, \'is_shown\': 0},\n    #   {\'id\': \'cd72bc923956952194468738123b7a5e\', \'name\': \'bar\', \'channel_number\': 2, \'signal_status\': 1, \'is_shown\': 1},\n    #   {\'id\': \'d2a2057d853438d9a5b4954baec136e3\', \'name\': \'baz\', \'channel_number\': 3, \'signal_status\': 0, \'is_shown\': 0}\n    # ]\n\n    call_status = await api.get_call_status(my_device_serial)\n    print(call_status)\n    # {\n    #   \'status\': \'idle\',\n    #   \'info\': {\n    #     \'building_number\': 0,\n    #     \'floor_number\': 0,\n    #     \'zone_number\': 0,\n    #     \'unit_number\': 0,\n    #     \'device_number\': 0,\n    #     \'device_type\': 0,\n    #     \'lock_number\': 0\n    #   }\n    # }\n    # can be "idle" / "ringing" / "call in progress" - see hikconnect/api.py:45\n    \n    await api.unlock(my_device_serial, 1)\n\n    # call this periodically at least once per 30 mins!\n    if api.is_refresh_login_needed():\n        await api.refresh_login()\n```\n',
    'author': 'Tomas Bedrich',
    'author_email': 'ja@tbedrich.cz',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://pypi.org/project/hikconnect',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
