# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['solsim']

package_data = \
{'': ['*']}

install_requires = \
['anchorpy>=0.6.4,<0.7.0',
 'numpy>=1.22.1,<2.0.0',
 'pandas>=1.4.0,<2.0.0',
 'tqdm>=4.62.3,<5.0.0']

setup_kwargs = {
    'name': 'solsim',
    'version': '0.1.5',
    'description': 'The Solana complex systems simulator.',
    'long_description': '# solsim\n\n<div align="center">\n    <img src="https://raw.githubusercontent.com/cavaunpeu/solsim/main/logo.png" width="70%" height="70%">\n</div>\n\n---\n\n[![Discord Chat](https://img.shields.io/discord/889577356681945098?color=blueviolet)](https://discord.gg/sxy4zxBckh)\n\nsolsim is the Solana complex systems simulator. It simulates behavior of dynamical systems—DeFi protocols, DAO governance, cryptocurrencies, and more—built on the [Solana](https://solana.com/) blockchain.\n\n## Philosophy\n\nDefine your system how you see fit.\n\nsolsim will simulate its behavior and collect its results in a structured, straightforward manner.\n\n## Usage\n\n1. Implement `initialStep` and `step` methods.\n2. From each, return the current state, i.e. a dictionary mapping variables to current values.\n3. Specify the variables you\'d like to "watch."\n4. Instantiate a Simulation, call .run().\n5. Receive a [pandas](https://pandas.pydata.org/) DataFrame containing values of "watched" variables at each step in time.\n\n### Example\n\n```python\nfrom anchorpy import Context\nfrom solana.keypair import Keypair\nfrom solsim.simulation import Simulation\n\n# Using solana\n\nclass SomeSolanaSystem(BaseSolanaSystem):\n    def __init__(self):\n        super().__init__("path/to/workspace")\n        self.account = Keypair()\n        self.pubkey = self.account.public_key\n        self.program = self.workspace["my_anchor_program"]  # solsim gives a Anchor program workspace (self.workspace).\n\n    async def initialStep(self):\n        self.program.rpc["initialize"]()  # Make RPC calls to your Anchor program.\n        await self.client.request_airdrop(self.pubkey, 10)  # solsim gives you a Solana API client (self.client).\n        return {"balance": await self.client.get_balance(self.pubkey)}\n\n    async def step(self, state, history):\n        self.program.rpc["submit_uniswap_trade"](\n            ctx=Context(accounts={"account": self.pubkey}, signers=[self.account])\n        )\n        return {"balance": await self.client.get_balance(self.account)}\n\n\nsimulation = Simulation(system=SomeSolanaSystem(), watchlist=("balance"), n_steps=5)\nresults = simulation.run()  # Returns pandas DataFrame of results.\n\n\n# Not using solana\n\nclass SomeSystem(BaseSystem):\n    def __init__(self, population):\n        self.pop = population\n\n    def initialStep(self):\n        return {"population": self.pop}\n\n    def step(self, state, history):\n        return {"population": state["population"] * 1.1}\n\n\nsimulation = Simulation(system=SomeSystem(), watchlist=("population"), n_steps=5)\nresults = simulation.run()\n```\n\n## Installation\n\nInstall [Anchor](https://project-serum.github.io/anchor/getting-started/installation.html#install-rust). Then,\n\n```sh\npip install solsim\n```\n\n### Development setup\n\nInstall [poetry](https://python-poetry.org/). Then,\n\n```sh\ngit clone https://github.com/cavaunpeu/solsim.git\ncd solsim\npoetry install\npoetry shell\n```\n\n## Detailed usage\n\n### Using Solana\n\nFirst, write your Solana program. solsim prefers you do this in [Anchor](https://project-serum.github.io/anchor/getting-started/introduction.html). Then,\n\n1. Write a system class that inherits from `BaseSolanaSystem`.\n2. Call `super().__init__("path/to/program")` in its `__init__`.\n3. Implement `initialStep` and `step` methods. (Since you\'ll interact with Solana asynchronously, these methods should be `async`.)\n\nIn `2.`, solsim exposes the following attributes to your system instance:\n\n- `self.workspace`: IDL clients for the Solana programs that comprise your system (via [anchorpy](https://github.com/kevinheavey/anchorpy)).\n\nFor example, these clients let you interact with your respective programs\' RPC endpoints.\n\n- `self.client`: a general Solana client (via [solana-py](https://github.com/michaelhly/solana-py)).\n\nThis client lets you interact with Solana\'s RPC endpoints. Documentation [here](https://michaelhly.github.io/solana-py/api.html#).\n\nFinally,\n\n1. Define a `watchlist`: variables (returned in `initialStep` and `step`) you\'d like to "watch."\n2. Instantiate and run your simulation, e.g. `Simulation(MySystem(), watchlist, n_steps=10).run()`.\n\n### Not using Solana\n\n1. Write a system class that inherits from `BaseSystem`.\n2. Implement `initialStep` and `step` methods.\n3. Define a `watchlist`.\n4. Instantiate and run your simulation.\n\n## Examples\n\n### Drunken escrow (w/ Solana)\n\nAgents are randomly paired to exchange random amounts of `foo_coin` and `bar_coin` via an Anchor escrow contract in each timestep.\n\n- Run: `python -m examples.drunken_escrow`.\n- Code: [here](https://github.com/cavaunpeu/solsim/tree/main/examples/drunken_escrow).\n- Expected output (numbers may vary):\n\n```\n(.venv) ➜  solsim git:(main) $ python -m examples.drunken_escrow\nWaiting for Solana localnet cluster to start (~10s) ...\nSteps completed: 100%|████████████████████████████████████████████████████████████████████████████████████| 4/4 [00:27<00:00,  6.82s/it]\n   step  mean_balance_spread  mean_swap_amount  num_swaps\n0    -1            40.000000         30.666667          3\n1     0            58.000000         12.000000          3\n2     1            60.666667          4.000000          3\n3     2            83.333333         21.500000          2\n```\n\n### Lotka-Volterra (w/o Solana)\n\nThe Lotka-Volterra model is a classic dynamical system in the field of ecology that tracks the evolution of interdependent predator and prey populations.\n\n- Run: `python -m examples.lotka_volterra`.\n- Code: [here](https://github.com/cavaunpeu/solsim/tree/main/examples/lotka_volterra).\n- Expected output:\n\n```\n(.venv) ➜  solsim git:(main) ✗ python -m examples.lotka_volterra\nSteps completed: 100%|█████████████████████████████████████████████████████████████████████████████████| 4/4 [00:00<00:00, 28581.29it/s]\n   step  food_supply  population_size\n0    -1     1000.000            50.00\n1     0      995.000            60.00\n2     1      989.000            69.95\n3     2      982.005            79.84\n```\n\nThis implementation inspired by [cadCAD Edu](https://www.cadcad.education/).\n\n## Inspiration\n\nsolsim humbly builds on the shoulders of the giants that are [cadCAD](https://github.com/cadCAD-org/cadCAD) and [tokenspice](https://github.com/tokenspice/tokenspice), among others.',
    'author': 'Will Wolf',
    'author_email': 'williamabrwolf@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/cavaunpeu/solsim',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
