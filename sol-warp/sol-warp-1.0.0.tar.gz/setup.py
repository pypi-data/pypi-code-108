# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['warp', 'warp.cli', 'warp.test_tool', 'warp.yul']

package_data = \
{'': ['*'],
 'warp': ['bin/linux/*',
          'bin/macos_10_14/*',
          'bin/macos_10_15/*',
          'bin/macos_11/*',
          'bin/macos_12/*',
          'cairo-src/*',
          'cairo-src/evm/*'],
 'warp.test_tool': ['example/contracts/*']}

install_requires = \
['cairo-lang==0.7.0',
 'click',
 'eth-abi',
 'importlib_resources',
 'pytest',
 'pytest-check',
 'pytest-xdist>=2.5.0,<3.0.0',
 'web3>=5.12']

entry_points = \
{'console_scripts': ['warp = warp.cli.cli:main']}

setup_kwargs = {
    'name': 'sol-warp',
    'version': '1.0.0',
    'description': 'A Solidity to Cairo Transpiler',
    'long_description': '# NOTE\n\nWarp is under heavy development and is currently not stable. A stable release will be released in the coming weeks.\n\n# Warp\n\nWarp brings Solidity to StarkNet, making it possible to transpile Ethereum smart contracts to Cairo, and use them on StarkNet.\n\n## Table of Contents :clipboard:\n\n- [NOTE](#note)\n- [Warp](#warp)\n  - [Table of Contents :clipboard:](#table-of-contents-clipboard)\n  - [Installation :gear:](#installation-gear)\n  - [Setting up autocompletion](#setting-up-autocompletion)\n  - [Usage :computer:](#usage-computer)\n  - [Solidity Constructs Currently Not Supported](#solidity-constructs-currently-not-supported)\n  - [Want to contribute? :thumbsup:](#want-to-contribute-thumbsup)\n  - [License](#license)\n\n## Installation :gear:\n\nPrerequisites:\nMake sure your Solidity compiler version is >= 0.8.0\n\nLinux:\n\n```\nsudo apt update\nsudo apt install software-properties-common\nsudo add-apt-repository ppa:deadsnakes/ppa\nsudo apt update\nsudo apt install -y python3.7\nsudo apt install -y python3.7-dev\nsudo apt install -y libgmp3-dev\nsudo apt install -y libboost-all-dev\nsudo apt-get install -y python3.7-venv\npython3.7 -m venv ~/warp\nsource ~/warp/bin/activate\npip install z3-solver\n```\n\nMacOs:\n\n```\nbrew install python@3.7\nbrew install gmp\nbrew install boost\nbrew install z3\npython3.7 -m venv ~/warp\nsource ~/warp/bin/activate\n```\n\nInstall Warp:\n\n```\npip install sol-warp\n```\n\n## Setting up autocompletion\n\nWarp comes with support for command line completion in bash, zsh, and fish\n\nfor bash:\n\n```\n eval "$(_WARP_COMPLETE=bash_source warp)" >> ~/.bashrc\n```\n\nfor zsh:\n\n```\n eval "$(_WARP_COMPLETE=zsh_source warp)" >> ~/.zshrc\n```\n\nfor fish:\n\n```\n_WARP_COMPLETE=fish_source warp > ~/.config/fish/completions/warp.fish\n```\n\n## Usage :computer:\n\nYou can transpile your Solidity contracts with:\n\n```\nwarp transpile FILE_PATH CONTRACT_NAME\n```\n\n`CONTRACT_NAME` is the name of the primary contract (non-interface, non-library, non-abstract contract) that you wish to transpile\n\nTo deploy the transpiled program to Starknet use:\n\n```\nwarp deploy CONTRACT.json\n```\n\nTo invoke a public/external method use:\n\n```\nwarp invoke --program CONTRACT.json --address ADDRESS --function FUNCTION_NAME --inputs \'INPUTS\'\n```\n\nHere\'s an example that shows you the format of the inputs for `inputs`:\n\nLet\'s say we want to call the following Solidity function in a contract that we\'ve transpiled & deployed on StarkNet:\n\n```solidity\nstruct Person {\n    uint age;\n    uint height;\n}\nfunction validate(address _ownerCheck, Person calldata _person, uint _ownerCellNumberCheck)\n  public view returns (bool) {\n    return (owner == _ownerCheck && ownerAge == _person.age\n        && ownerCellNumber == _ownerCellNumberCheck);\n}\n```\n\nThe command to call this function would be:\n\n```bash\nwarp invoke --program CONTRACT.json --address ADDRESS --function validate \\\n        --inputs \'[0x07964d2123425737cd3663bec47c68db37dc61d83fee74fc192d50a59fb7ab56,\n        (26, 200), 7432533831]\'\n```\n\nThe `--inputs` flag, if not empty, should always be an \'array\'. As you can see, we have\npassed the struct fields as a tuple, their order should be the same as their\ndeclaration order (i.e `age` first, `person` second). If the first argument to the\n`validate` function was an array of uint\'s, then we\'d pass it in as you\'d expect:\n\n```bash\n--inputs = \'[[42,1722,7], (26, 200), 7432533831]\'\n```\n\nIf you\'re passing in the `bytes` Solidity type as an argument, use the python syntax, for example:\n```bash\n--inputs = \'[[10,20], b"\\x01\\x02"]\'\n```\n\nYou can check the status of your transaction with:\n\n```\nwarp status TX_HASH\n```\n\n## Testing with Warp\n\nYou\'ll find an example of how to write tests in your solidity contract, and then call `warp test` to run them in `src/warp/test_tool/example`.\nFor the tests to work, you\'ll need to run `warp test` from a parent directory where your solidity contracts are in a directory named `contracts`, \nas per the example mentioned above.\n\n## Solidity Constructs Currently Not Supported\n\n\n|  Support Status                 | Symbol            | \n|:-------------------------------:|:-----------------:|\n| Will likely never be supported  | :x:               |\n| Support will land soon          | :hammer_and_pick: |\n| Will be supported in the future | :exclamation:     |\n| Currently Unkown                | :question:        |\n\n<center>\n\n| Solidity          |  Support Status                 |\n|:-----------------:|:-------------------------------:|\n| try/catch         |  :question:                     |\n| msg.value         |  :x:                            |\n| tx.origin         |  :exclamation:                  |\n| tx.gasprice       |  :question:                     |\n| block.basefee     |  :x:                            |\n| block.chainid     |  :exclamation:                  |\n| block.coinbase    |  :question:                     |\n| block.difficulty  |  :x:                            |\n| block.gaslimit    |  :question:                     |\n| gasleft()         |  :question:                     |\n| functions as data |  :x:                            |\n| precompiles       |  :exclamation:                  |\n| create/create2    |  :exclamation:                  |\n| Selfdestruct      |  :x:                            |\n| BlockHash         |  :exclamation:                  |\n\n\n| Yul               |  Support Status                 |\n|:-----------------:|:-------------------------------:|\n| loadimmutable     |  :hammer_and_pick:              |\n| setimmutable      |  :hammer_and_pick:              |\n| linkersymbol      |  :question:                     |\n| codeCopy          |  :question:                     |\n| codeSize          |  :question:                     |\n\nRun `solc --optimize --ir-optimized <file>` to see if your Solidity results in\nany of these YUL constructs.\n\n</center>\n\n## Want to contribute? :thumbsup:\n\nYour contributions are always welcome, see [contribution guidelines](CONTRIBUTING.md).\n\n## License\n\n[Apache License](LICENSE) Version 2.0, January 2004.\n',
    'author': 'Nethermind',
    'author_email': 'hello@nethermind.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/NethermindEth/warp',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<3.10',
}


setup(**setup_kwargs)
