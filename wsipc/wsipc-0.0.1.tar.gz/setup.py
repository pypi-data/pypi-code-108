# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['wsipc']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.8.1,<4.0.0']

setup_kwargs = {
    'name': 'wsipc',
    'version': '0.0.1',
    'description': 'Async Python IPC using WebSockets',
    'long_description': '# wsipc\n\nAsync Python IPC using WebSockets\n\n## Server Example (Simple Broker)\n\n```py\nfrom asyncio import run\n\nfrom wsipc import WSIPCServer\n\nserver = WSIPCServer(heartbeat=45)\n\nrun(server.start(block=True))\n```\n\n## Client Example\n\n```py\nfrom asyncio import create_task, run, sleep\n\nfrom wsipc import WSIPCClient\n\n\nclient = WSIPCClient()\n\n@client.listener()\nasync def on_message(message):\n    print(message)\n\n@client.listener()\ndef sync_listener(message):\n    print(message)\n\nasync def main() -> None:\n    create_task(client.connect())\n\n    await client.connected.wait()\n\n    await client.send("Hello World!")\n\n    await sleep(1)\n\n    await client.close()\n\nrun(main())\n```\n',
    'author': 'vcokltfre',
    'author_email': 'vcokltfre@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/vcokltfre/wsipc',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
