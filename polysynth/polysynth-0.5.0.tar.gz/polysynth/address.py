from typing import Dict

from web3 import Web3
from web3.types import ChecksumAddress


address_mumbai: Dict[str, ChecksumAddress] = {
    k: Web3.toChecksumAddress(v)
    for k, v in {
        "StableToken": "0x917A88248F0C798A11Cf5513bA36082B1700782E",
        "Manager": "0x612bDe1DEB6be82a29D095F935A2f46B87Ab0853",
        "Amm_eth-usdc": "0xcD895Fa433ABE5111501C5e23A9BeCbe0f19A512",
        "Amm_btc-usdc": "0xB15b755E9172A2fc0A804CeE8Edd5Ac384794dea",
        "Amm_matic-usdc": "0xc71349eBfAe2150FdA5f9bDA3E85d02916485acE",
        "AmmReader": "0x5d4dA7a1833b72Aa9492fc75307f74b365D75E55"
    }.items()
}
