def to_bytes(x, encoding="utf-8"):
    if isinstance(x, str):
        x = x.encode(encoding)
    return x

def to_str(x, encoding="utf-8"):
    if isinstance(x, bytes):
        x = x.decode(encoding)
    return x

