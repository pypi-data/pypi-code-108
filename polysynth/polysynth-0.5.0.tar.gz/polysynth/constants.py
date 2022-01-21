# see: https://chainid.network/chains/
_netid_to_name = {
    80001: "mumbai",
    31337: "local"
}

_contract_addresses_proxy_v1 = {
    "mumbai": {
        "StableToken": "0x917A88248F0C798A11Cf5513bA36082B1700782E",
        "Manager": "0x612bDe1DEB6be82a29D095F935A2f46B87Ab0853",
        "Amm_eth-usdc": "0xcD895Fa433ABE5111501C5e23A9BeCbe0f19A512",
        "Amm_btc-usdc": "0xB15b755E9172A2fc0A804CeE8Edd5Ac384794dea",
        "Amm_matic-usdc": "0xc71349eBfAe2150FdA5f9bDA3E85d02916485acE",
        "AmmReader": "0x5d4dA7a1833b72Aa9492fc75307f74b365D75E55"
    },
    "local": {
        "StableToken": "0x5FbDB2315678afecb367f032d93F642f64180aa3",
        "Manager": "0x5FC8d32690cc91D4c39d9d3abcBD16989F875707",
        "Amm_eth-usdc": "0x0DCd1Bf9A1b36cE34237eEaFef220932846BCD82",
        "Amm_btc-usdc": "0x9A9f2CCfdE556A7E9Ff0848998Aa4a0CFD8863AE",
        "Amm_matic-usdc": "0x59b670e9fA9D0A427751Af201D676719a970857b",
        "AmmReader": "0xB7f8BC63BbcaD18155201308C8f3540b07f84F5e"
    },
}

_contract_addresses_oracle = {
    "mumbai": {
        "eth-usdc": "0x0715A7794a1dc8e42615F059dD6e406A6594651A",
        "btc-usdc": "0x007A22900a3B98143368Bd5906f8E17e9867581b",
        "matic-usdc": "0xd0D5e3DB44DE05E9F294BB0a3bEEaF030DE24Ada",
    },
    "local": {
        "eth-usdc": "0x0715A7794a1dc8e42615F059dD6e406A6594651A",
        "btc-usdc": "0x007A22900a3B98143368Bd5906f8E17e9867581b",
        "matic-usdc": "0xd0D5e3DB44DE05E9F294BB0a3bEEaF030DE24Ada",
    },
    "matic": {
        "eth-usdc": "0xF9680D99D6C9589e2a93a78A04A279e509205945",
        "btc-usdc": "0xc907E116054Ad103354f2D350FD2514433D57F6f",
        "matic-usdc": "0xAB594600376Ec9fD91F8e885dADF0CE036862dE0",
        "sol-usdc": "0x10C8264C0935b3B9870013e057f330Ff3e9C56dC",
        "dot-usdc": "0xacb51F1a83922632ca02B25a8164c10748001BdE",
    }
}