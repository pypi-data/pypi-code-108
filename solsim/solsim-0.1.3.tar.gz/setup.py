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
    'version': '0.1.3',
    'description': 'The Solana complex systems simulator.',
    'long_description': '# solsim\n\n<div align="center">\n    <img src="https://raw.githubusercontent.com/cavaunpeu/solsim/add-readme/logo.png" width="70%" height="70%">\n</div>\n\n---\n\n[![Discord Chat](https://img.shields.io/discord/889577356681945098?color=blueviolet)](https://discord.gg/sxy4zxBckh)\n\nsolsim is the Solana complex systems simulator. It simulates behavior of dynamical systems—e.g. DeFi protocols, DAO governance, cryptocurrencies—built on the [Solana](https://solana.com/) blockchain.\n\n## Philosophy\n\nDefine your system how you see fit.\n\nsolsim will simulate its behavior and its collect results in a straightforward, structured manner.\n\n## Usage\n\n1. Implement `initialStep` and `step` methods how you see fit.\n2. From each, return a dictionary mapping variables to current values.\n3. Specify the variables you\'d like to "watch."\n4. Instantiate a `Simulation`, call `.run()`.\n5. Receive a [pandas](https://pandas.pydata.org/) DataFrame of results.\n\n## Installation\n\n```sh\npip install solsim\n```\n\n### Development setup\n\nFirst, install [poetry](https://python-poetry.org/).\n\nThen:\n\n```sh\ngit clone https://github.com/cavaunpeu/solsim.git\ncd solsim\npoetry install\npoetry shell\n```\n\n## Detailed usage\n\n### Systems using Solana\n\nFirst, write the Solana programs in Rust or [Anchor](https://project-serum.github.io/anchor/getting-started/introduction.html) that comprise your system.\n\nNext, copy the generated idl.json for each into a directory (e.g. named `workspace`) built as such:\n\n```\nworkspace\n└── target\n    └── idl\n        ├── program1.json\n        ├── program2.json\n        └── program3.json\n```\n\nThen,\n\n1. Build a system class that inherits from `BaseSolanaSystem`.\n2. Implement `initialStep` and `step` methods.\n3. Call `super().__init__("workspace")` in its `__init__`.\n\nIn `3`, solsim exposes the following attributes to your system:\n\n- `self.workspace`: IDL clients for the Solana programs that comprise your system (via [anchorpy](https://github.com/kevinheavey)).\n\nFor example, these clients let you interact with your respective programs\' RPC endpoints.\n\n- `self.client`: a general Solana client (via [solana-py](https://github.com/michaelhly/solana-py)).\n\nThis client lets you interact with Solana\'s RPC endpoints. Documentation [here](https://michaelhly.github.io/solana-py/api.html#).\n\nFinally,\n\n1. Define a `watchlist`: variables (returned in `initialStep` and `step`) you\'d like to "watch."\n2. Instantiate and run your simulation, e.g. `Simulation(MySystem(), watchlist, n_steps=10).run()`.\n\n#### Example\n\nSee the [drunken escrow](https://github.com/cavaunpeu/solsim/tree/main/examples/drunken_escrow) system.\n\n### Systems not using Solana\n\n1. Build a system class that inherits from `BaseSystem`.\n2. Implement `initialStep` and `step` methods.\n3. Define a `watchlist`: variables (returned in `initialStep` and `step`) you\'d like to "watch."\n4. Instantiate and run your simulation, e.g. `Simulation(MySystem(), watchlist, n_steps=10).run()`.\n\n#### Example\n\nSee the [Lotka-Volterra](https://github.com/cavaunpeu/solsim/tree/main/examples/drunken_escrow) system, inspired by [cadCAD Edu](https://www.cadcad.education/).',
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
