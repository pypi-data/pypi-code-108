def format_symbol(symbol: str):
    return symbol.upper().replace("/", "_")


def format_market(market: str):
    return market.lower().replace("/", "_")


def format_websocket_market(market: str):
    return market.lower().replace("/", "")


def format_websocket_user_market(market: str):
    return market.lower().removesuffix("default")
