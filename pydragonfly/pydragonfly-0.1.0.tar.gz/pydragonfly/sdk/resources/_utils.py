def omit_keys(d: dict, keys: list) -> dict:
    return {k: v for k, v in d.items() if k not in keys}
