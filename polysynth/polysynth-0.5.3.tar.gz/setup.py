# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['polysynth']

package_data = \
{'': ['*'], 'polysynth': ['assets/*']}

install_requires = \
['beartype>=0.8.0,<0.9.0', 'web3>=5.24.0,<6.0.0']

entry_points = \
{'console_scripts': ['polypy = polysynth:main']}

setup_kwargs = {
    'name': 'polysynth',
    'version': '0.5.3',
    'description': 'Official Python wrapper for the Polysynth platform',
    'long_description': '# Polysynth Python SDK\n\nThe official Python client for [Polysynth](https://polysynth.com/).\n\nDocumentation is available [here](https://docs.polysynth.com/developer-resources/python-sdk).\n\n## Getting Started\nThis library attempts to present a clean interface to Polysynth, but in order to use it to its full potential, you must familiarize yourself with the official Polysynth documentation:\n- Installation\n- Quoting Prices\n- Making Trades\n- Managing Collaterals\n- Ratios\n\n### Installation\nYou can install the latest release from PyPI, or install the latest commit directly from git:\n- Install the latest release from PyPI:\n ``` pip install polysynth```\n\n- Install from git:\n ``` pip install git+https://github.com/kryptolabs/polysynth-python.git```\n\n- Clone and install with poetry:\n```\ngit clone https://github.com/kryptolabs/polysynth-python.git\ncd polysynth-python\npoetry install\n```\n### Quoting Prices\n##### input_price\nReturns the amount of ETH you get for 1 USDP\n```\nclient.input_price("ETH-USDC", "BUY", 1)\n```\n##### output_price\nReturns the amount of USDP you need to pay to get 1000 ETH\n```\nclient.output_price("ETH-USDC", “BUY”, 1000)\n```\n\n### Making Trades\n##### open_position\nOpen a long position against 1000 USDP worth ETH with a leverage of 1x and slippage  tolerance of 0%\n ```\nclient.open_position("ETH-USDC", “BUY”, 1000, 1, 0)\n```\n##### close_position\nCloses a trader’s all positions for ETH with zero slippage tolerance\n```\nclient.close_position("ETH-USDC", 0)\n```\n\n### Managing Collaterals\n##### add_collateral\nAdd 1000 USDP worth collateral in ETH AMM\n```\nclient.add_collateral("ETH-USDC", 1000)\n```\n\n##### remove_collateral\nRemove 500 USDP worth collateral from ETH AMM\n```\nclient.remove_collateral("ETH-USDC", 500)\n```\n\n### Ratios\n##### fluctuation_limit_ratio\nGet fluctuation limit ratio of ETH market\n```\nclient.fluctuation_limit_ratio("ETH-USDC")\n```\n\n##### trade_limit_ratio\nGet trade limit ratio of ETH market\n```\nclient.trade_limit_ratio("ETH-USDC")\n```\n\n##### collateral_ratio\nGet collateral ratio of ETH market\n```\nclient.collateral_ratio("ETH-USDC")\n```\n\n##### fee_ratio\nGet fee ratio of the platform\n```\nclient.fee_ratio()\n```\n\n##### init_collateral_ratio\nGet initial collateral ratio of the platform\n```\nclient.init_collateral_ratio()\n```\n\n##### liquidation_fee_ratio\nGet liquidation fee ratio of the platform\n```\nclient.liquidation_fee_ratio()\n```\n\n##### maintenance_collateral_ratio\nGet maintenance collateral ratio of the platform\n```\nclient.maintenance_collateral_ratio()\n```\n\n##### partial_liquidation_ratio\nGet partial liquidation ratio of the platform\n```\nclient.partial_liquidation_ratio()\n```\n\n\n### Testing\nTo run the full test suite, in the project directory set the `PROVIDER` env variable to a  provider, and run:\n\n```\npoetry install\nexport PROVIDER= # URL of provider, e.g. https://mainnet.infura.io/v3/...\npoetry shell\npoetry run pytest\n```\n\n### Publish to pip\nTo build and publish the package to pip,run:\n\n```\npoetry shell\npoetry build\npoetry publish\n```\n\n## Authors\n* [Arpit Singh](https://github.com/gyan/)\n* [Paritosh Gupta](https://github.com/mavvverick)',
    'author': 'Arpit Singh',
    'author_email': 'gyan@github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/kryptolabs/polysynth-python',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7.2,<4.0.0',
}


setup(**setup_kwargs)
