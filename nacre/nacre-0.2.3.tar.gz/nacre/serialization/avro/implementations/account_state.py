from typing import Dict

import orjson
from nautilus_trader.model.c_enums.account_type import AccountTypeParser
from nautilus_trader.model.events.account import AccountState


"""
AccountSnapshot for analysis
Expect info structure:
    "info": {
        "positions": [
            {
                "": "",
            },
            {},
        ],
        "equity": 0,
    }
"""


def serialize(state: AccountState):
    base = {
        "account_id": state.account_id.value,
        "account_type": AccountTypeParser.to_str_py(state.account_type),
        "base_currency": state.base_currency.code if state.base_currency else None,
        "reported": state.is_reported,
        "event_id": state.id.value,
        "ts_event": state.ts_event,
        "ts_init": state.ts_init,
    }

    balances = []
    for balance in state.balances:
        balances.append(
            {
                "currency": balance.currency.code,
                "total": balance.total.as_double(),
                "locked": balance.locked.as_double(),
                "free": balance.free.as_double(),
            }
        )

    base["balances"] = orjson.dumps(balances).decode("utf-8")
    positions = state.info.get("positions", [])
    base["positions"] = orjson.dumps(positions).decode("utf-8")
    base["equity"] = state.info.get("equity", 0)
    return base


def deserialize(data: Dict):
    # data["balances"] = data["balances"].encode()
    # data["info"] = data["info"].encode()
    # return AccountState.from_dict(data)
    pass
