from dataclasses import dataclass


@dataclass
class HandshakeParams(object):
    key: str

    def __init__(self, key):
        self.key: str = f"-----BEGIN PUBLIC KEY-----\n{key}\n-----END PUBLIC KEY-----\n"
