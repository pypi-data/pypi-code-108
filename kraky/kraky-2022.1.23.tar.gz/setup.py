# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['kraky']

package_data = \
{'': ['*']}

install_requires = \
['httpx>=0.21.0,<0.22.0',
 'tox>=3.24.4,<4.0.0',
 'typer>=0.4.0,<0.5.0',
 'websockets>=10.0,<11.0']

entry_points = \
{'console_scripts': ['kraky = kraky.cli:app']}

setup_kwargs = {
    'name': 'kraky',
    'version': '2022.1.23',
    'description': 'Python client for Kraken API REST and Kraken Websockets API using httpx and websockets. Supports both sync and async for API REST.',
    'long_description': '[![Total alerts](https://img.shields.io/lgtm/alerts/g/Atem18/kraky.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/Atem18/kraky/alerts/)\n[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/Atem18/kraky.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/Atem18/kraky/context:python)\n\n# Kraky\nPython client for Kraken API REST and Kraken Websockets API using httpx and websockets.\nSupports both sync and async for API REST.\n\n## Installation \n    pip install kraky\n\n## Docs\n\n    https://kraky.readthedocs.io/en/latest/\n\n## Usage\n\n### CLI\n\nKraky provides a CLI that matches the API function names and args.\n\nYou can use it like the following:\n\n```bash\nkraky get_ohlc_data pair=XBTUSD interval=240\n```\n\nYou can replace get_ohlc_data by any kraky API function and pair=XBTUSD or interval=240 by any function argument.\nPlease respect the format key=value.\n\nIt also supports .env files so you can also create a .env file with your api_key and secret and kraky will pick them up.\n\nExample:\n```bash\nKRAKEN_API_KEY=""\nKRAKEN_SECRET=""\n```\n\n### Sync REST API\n```python\nfrom kraky import KrakyApiClient\n\n\ndef get_web_sockets_token():\n    kraken_api_key = ""\n    kraken_secret = ""\n    kraky_api_client = KrakyApiClient(\n        api_key=kraken_api_key, secret=kraken_secret\n    )\n\n    ws_token = self.kraky_api_client.get_web_sockets_token()\n    return ws_token\n\nget_web_sockets_token()\n```\n\n### Async REST API\n```python\nfrom kraky import KrakyApiAsyncClient\n\n\nasync def get_web_sockets_token():\n    kraken_api_key = ""\n    kraken_secret = ""\n    kraky_api_client = KrakyApiAsyncClient(\n        api_key=kraken_api_key, secret=kraken_secret\n    )\n\n    ws_token = await self.kraky_api_client.get_web_sockets_token()\n    return ws_token\n\nasyncio.run(get_web_sockets_token)\n```\n\n### Websocket\n\n```python\nimport asyncio\nfrom kraky import KrakyApiAsyncClient, KrakyWsClient\n\n\nasync def get_web_sockets_token():\n    kraken_api_key = ""\n    kraken_secret = ""\n    kraky_api_client = KrakyApiAsyncClient(\n        api_key=kraken_api_key, secret=kraken_secret\n    )\n\n    ws_token = await self.kraky_api_client.get_web_sockets_token()\n    return ws_token\n\n\nasync def public_handler(response):\n    print(response)\n\n\nasync def private_handler(response):\n    print(response)\n\n\nasync def main():\n\n    interval = 30\n\n    ws_pairs = ["XBT/USD", "ETH/USD"]\n\n    ws_token = await get_ws_token()\n\n    kraky_public_ws_client = KrakyWsClient("production")\n    kraky_private_ws_client = KrakyWsClient("production-auth")\n\n    asyncio.create_task(\n        kraky_public_ws_client.connect(public_handler, connection_name="public")\n    )\n\n    asyncio.create_task(\n        kraky_private_ws_client.connect(private_handler, connection_name="private")\n    )\n\n    await kraky_public_ws_client.subscribe(\n        {"name": "ohlc", "interval": interval},\n        ws_pairs,\n        connection_name="public",\n    )\n\n    await kraky_private_ws_client.subscribe(\n        {\n            "interval": interval,\n            "token": ws_token,\n            "name": "openOrders",\n        },\n        connection_name="private",\n    )\n\n\nif __name__ == "__main__":\n    loop = asyncio.get_event_loop()\n    loop.create_task(main())\n    loop.run_forever()\n\n```\n\n## Compatibility\n\n- Python 3.7 and above\n\n## Licence\n\nMIT License\n',
    'author': 'Atem18',
    'author_email': 'contact@atemlire.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://kraky.readthedocs.io/en/latest',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
