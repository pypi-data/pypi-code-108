# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['starknet_devnet']

package_data = \
{'': ['*']}

install_requires = \
['Flask[async]>=2.0.2,<3.0.0', 'cairo-lang==0.7.0', 'flask-cors>=3.0.10,<4.0.0']

entry_points = \
{'console_scripts': ['starknet-devnet = starknet_devnet.server:main']}

setup_kwargs = {
    'name': 'starknet-devnet',
    'version': '0.1.13',
    'description': 'A local testnet for Starknet',
    'long_description': "## Introduction\nA Flask wrapper of Starknet state. Similar in purpose to Ganache.\n\nAims to mimic Starknet's Alpha testnet, but with simplified functionality.\n\n## Install\n```text\npip install starknet-devnet\n```\n\n## Requirements\nWorks with Python versions <=3.9.7.\n\nOn Ubuntu/Debian, first run:\n```text\nsudo apt install -y libgmp3-dev\n```\n\nOn Mac, you can use `brew`:\n```text\nbrew install gmp\n```\n\n## Disclaimer\n- Devnet should not be used as a replacement for Alpha testnet. After testing on Devnet, be sure to test on testnet!\n- Hash calculation of transactions and blocks differs from the one used in Alpha testnet.\n- Specifying a block by its hash/number is not supported. All interaction is done with the latest block.\n- Read more in [interaction](#interaction-api).\n\n## Run\nInstalling the package adds the `starknet-devnet` command.\n```text\nusage: starknet-devnet [-h] [-v] [--host HOST] [--port PORT]\n\nRun a local instance of Starknet Devnet\n\noptional arguments:\n  -h, --help            show this help message and exit\n  -v, --version         Print the version\n  --host HOST           Specify the address to listen at; defaults to localhost (use the address the program outputs on start)\n  --port PORT, -p PORT  Specify the port to listen at; defaults to 5000\n```\n\n## Run - Docker\nDevnet is available as a Docker container ([shardlabs/starknet-devnet](https://hub.docker.com/repository/docker/shardlabs/starknet-devnet)):\n```text\ndocker pull shardlabs/starknet-devnet\n```\n\nThe server inside the container listens to the port 5000, which you need to publish to a desired `<PORT>` on your host machine:\n```text\ndocker run -it -p [HOST:]<PORT>:5000 shardlabs/starknet-devnet\n```\nE.g. if you want to use your host machine's `127.0.0.1:5000`, you need to run:\n```text\ndocker run -it -p 127.0.0.1:5000:5000 shardlabs/starknet-devnet\n```\nYou may ignore any address-related output logged on container startup (e.g. `Running on all addresses` or `Running on http://172.17.0.2:5000`). What you will use is what you specified with the `-p` argument.\n\nIf you don't specify the `HOST` part, the server will indeed be available on all of your host machine's addresses (localhost, local network IP, etc.), which may present a security issue if you don't want anyone from the local network to access your Devnet instance.\n\n## Interaction\n- Interact with Devnet as you would with the official Starknet [Alpha testnet](https://www.cairo-lang.org/docs/hello_starknet/amm.html?highlight=alpha#interaction-examples).\n- The exact underlying API is not exposed for the same reason Alpha testnet does not expose it.\n- The following Starknet CLI commands are supported:\n  - `call`\n  - `deploy`\n  - `get_block`\n  - `get_code`\n  - `get_storage_at`\n  - `get_transaction`\n  - `invoke`\n  - `tx_status`\n  - `get_transaction_receipt`\n- The following Starknet CLI commands are **not** supported:\n  - `get_contract_addresses` - L1-L2 interaction is currently not supported\n\n## Hardhat integration\n- If you're using [the Hardhat plugin](https://github.com/Shard-Labs/starknet-hardhat-plugin), see [here](https://github.com/Shard-Labs/starknet-hardhat-plugin#testing-network) on how to edit its config file to integrate Devnet.\n\n## Development - Prerequisite\nIf you're a developer willing to contribute, be sure to have installed [Poetry](https://pypi.org/project/poetry/).\n\n## Development - Run\n```text\npoetry run starknet-devnet\n```\n\n## Development - Test\nWhen running tests locally, do it from the project root.\n\nSetup an example project by running:\n```text\n./scripts/setup_example.sh\n```\n\nTo see if Devnet can interact with starknet CLI commands, run:\n```text\npython3 -m test.test_cli\npython3 -m test.test_cli_auth\n```\n\nTo see if Devnet can interact with the Hardhat plugin, run:\n```text\npython3 -m test.test_plugin\n```\n\n## Development - Build\n```text\npoetry build\n```\n",
    'author': 'FabijanC',
    'author_email': 'fabijan.corak@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Shard-Labs/starknet-devnet',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
