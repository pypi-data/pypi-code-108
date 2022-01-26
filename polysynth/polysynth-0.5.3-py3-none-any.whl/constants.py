# see: https://chainid.network/chains/
_netid_to_name = {
    80001: "mumbai",
    31337: "local"
}

_contract_addresses_proxy_v1 = {
    "mumbai": {
        "StableToken": "0x27f43eF37bc44120eDD91626f40C6DFa8908300C",
        "Manager": "0x25074928fA2cDd06Fb9f0902d710f7EDB494dbe2",
        "Amm_eth-usdc": "0x9e7225628bB6f9F437F123287602f59d705c8AA1",
        "Amm_btc-usdc": "0x40Ff56e22D26B41F13f79D61311e7DA605C0c4c2",
        "Amm_matic-usdc": "0xaB0BcF1F2f24145EcB2EAF3A11B8E1A25A839de7",
        "AmmReader": "0x410325f7A08FD56374a822db318E2593c9e5F5C8"
    },
    "local": {
        "StableToken": "0x5FbDB2315678afecb367f032d93F642f64180aa3",
        "Manager": "0x5FC8d32690cc91D4c39d9d3abcBD16989F875707",
        "Amm_eth-usdc": "0x0DCd1Bf9A1b36cE34237eEaFef220932846BCD82",
        "Amm_btc-usdc": "0x9A9f2CCfdE556A7E9Ff0848998Aa4a0CFD8863AE",
        "Amm_matic-usdc": "0x59b670e9fA9D0A427751Af201D676719a970857b",
        "AmmReader": "0xB7f8BC63BbcaD18155201308C8f3540b07f84F5e"
    }
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
    }
}