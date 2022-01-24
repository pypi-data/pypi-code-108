import hashlib


def md5enc(buf):
    if isinstance(buf, str):
        buf = bytes(buf, "utf-8")

    assert isinstance(buf, bytes)

    return hashlib.md5(buf).hexdigest()
