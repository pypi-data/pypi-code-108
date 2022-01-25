import monocypher
from typing import Union
from hashlib import md5
from l0n0ltcp.sym_enc_base import SymEncBase

class SymEncChaCha20(SymEncBase):
    def __init__(self, key: Union[bytes, str]) -> None:
        if isinstance(key, str):
            key = key.encode()
        m = md5()
        m.update(key)
        self.key = m.hexdigest().encode()
        self.nonce = self.key[-8:]

    def encode(self, data: bytes) -> bytearray:
        return monocypher.chacha20(self.key, self.nonce, data)

    def decode(self, data: bytes) -> bytearray:
        return monocypher.chacha20(self.key, self.nonce, data)
