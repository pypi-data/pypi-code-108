from typing import Dict

from web3 import Web3
from web3.types import ChecksumAddress


address_mumbai: Dict[str, ChecksumAddress] = {
    k: Web3.toChecksumAddress(v)
    for k, v in {
        "StableToken": "0x27f43eF37bc44120eDD91626f40C6DFa8908300C",
        "Manager": "0x25074928fA2cDd06Fb9f0902d710f7EDB494dbe2",
        "Amm_eth-usdc": "0x9e7225628bB6f9F437F123287602f59d705c8AA1",
        "Amm_btc-usdc": "0x40Ff56e22D26B41F13f79D61311e7DA605C0c4c2",
        "Amm_matic-usdc": "0xaB0BcF1F2f24145EcB2EAF3A11B8E1A25A839de7",
        "AmmReader": "0x410325f7A08FD56374a822db318E2593c9e5F5C8"
    }.items()
}
}
