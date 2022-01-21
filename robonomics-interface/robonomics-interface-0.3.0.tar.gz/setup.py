# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['robonomicsinterface']

package_data = \
{'': ['*']}

install_requires = \
['substrate-interface>=1.1.7,<2.0.0']

setup_kwargs = {
    'name': 'robonomics-interface',
    'version': '0.3.0',
    'description': 'Robonomics wrapper over https://github.com/polkascan/py-substrate-interface created to facilitate programming with Robonomics',
    'long_description': '# robonomics-interface\nThis is a simple wrapper over https://github.com/polkascan/py-substrate-interface used to facilitate writing code for applications using Robonomics.\n\nRobonomics project: https://robonomics.network/\n\nRobonomics parachain dapp: https://parachain.robonomics.network/\n_______\n# Installation \n```bash\npip3 install robonomics-interface\n```\n# Usage\n*More info may be found in docstrings in the source code*\n```python\nimport robonomicsinterface as RI\n```\n## Initialization\n```python\ninterface = RI.RobonomicsInterface()\n```\nBy default, you will only be able to fetch Chainstate info from Frontier parachain and use PubSub pattern.  \n\nYou can specify another `node address` (e.g. local), `seed` to sign extrinsics (more on that [later](#extrinsics)) \nand custom `registry types`. \n\nBy default, in the Frontier parachain there is a 10 minutes timeout, after which connection becomes broken.\nBut there is also a `keep_alive` option that keeps websocket opened with `ping()` calls in an\nasynchronous event loop. Watch out using `asyncio` with this option since `keep_alive` tasks are added to main thread\nevent loop, **which is running in another thread.** More on that in a docstring of the method.\n\n\n## Simple case: fetch Chainstate\nHere, no need to pass any arguments, by\n```python\ninterface = RI.RobonomicsInterface()\n```\nyou will be able to read any Chainstate info from the Frontier parachain:\n```python\nnum_dt = interface.custom_chainstate("DigitalTwin", "Total")\n```\nyou can also specify an argument for the query. Several arguments should be put in a list.\n\nThere is a dedicated function to obtain **Datalog**:\n```python\nrecord = interface.fetch_datalog(<ss58_addr>)\n```\nThis will give you the latest datalog record of the specified account with its timestamp. You may pass an index argument to fetch specific record. If you create an interface with a provided seed, you\'ll be able to fetch self-datalog calling `fetch_datalog` with no arguments (or just the `index` argument). \n\n## Extrinsics\n**Providing seed** (any raw or mnemonic) while initializing **will let you create and submit extrinsics**:\n```python\ninterface = RI.RobonmicsInterface(seed:str = <seed>)\nhash = interface.custom_extrinsic("DigitalTwin", "create")\n```\n`hash` here is the transaction hash of the succeeded extrinsic. You can also specify arguments for the extrinsic as a dictionary.\n\nThere are dedicated functions for recording datalog and sending launch commands:\n```python\ninterface.record_datalog("Hello, Robonomics")\ninterface.send_launch(<target_addr>, True)\n```\nCurrent nonce definition and manual nonce setting is also possible.\n\n## Robonomics Web Services (RWS)\nThere are as well dedicated methods for convenient usage of RWS.\n- Chainstate functions `auctionQueue`, `auction` to examine subscriptions auctions:\n```python\ninterface.rws_auction_queue()\ninteface.rws_auction(<auction_index>)\n```\n- Extrinsincs: `bid`, `set_devices` and, the most important, `call`\n```python\ninterface.rws_bid(<auction_index>, <amount_weiners>)\ninterface.rws_set_devices([<ss58_addr>, <ss58_addr>])\ninterface.rws_custom_call(<subscription_owner_addr>,\n                           <call_module>,\n                           <call_function>,\n                           <params_dict>)\n```\nThere are as well dedicated `datalog` and `launch` functions for RWS-based transactions.\n```python\ninterface.rws_record_datalog(<subscription_owner_addr>, <data>)\ninterface.rws_send_launch(<subscription_owner_addr>, <target_addr>, True)\n```\n\n## Subscriptions\nThere is a subscriptions functional implemented. When initiated, blocks thread and processes new events with a user-passed \ncallback function. Pay attention that this callback may only accept one argument - the event data. Up to now, the only supported \nevents are `NewRecord`, `NewLaunch`, `Transfer`\n```python\nfrom robonomicsinterface import RobonomicsInterface, Subscriber, SubEvent\n\ndef callback(data):\n    print(data)\n\ninterface = RobonomicsInterface()\nsubscriber = Subscriber(interface, SubEvent.NewLaunch, callback, <ss58_addr>)\n```\n\n## JSON RPC\n*WARNING: THIS MODULE IS UNDER CONSTRUCTIONS, USE AT YOUR OWN RISK! TO BE UPDATED SOON.*  \nThere is a way to implement robonomics pubsub rpc calls:\n\n```python3\ninterface = RI.RobonomicsInterface()\npubsub = PubSub(interface)\npubsub.peer()\n```\n\nThis is an evolving package, it may have errors and lack of functionality, fixes are coming.\nFeel free to open issues when faced a problem.',
    'author': 'Pavel Tarasov',
    'author_email': 'p040399@outlook.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Multi-Agent-io/robonomics-interface',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>3.6,<4.0',
}


setup(**setup_kwargs)
