# -*- coding: utf-8 -*-
"""
pyape.util.encrypt
~~~~~~~~~~~~~~~~~~~

用于加密的封装
"""

import re
import base64

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

ZERO_RE = re.compile(r'[\x00-\x1F]+$')

class AES_CBC(object):

    def __init__(self, key, iv):
        self._cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())

    def encrypt(self, plain_txt):
        return None

    def decrypt(self, encrypted_bytes):
        decryptor = self._cipher.decryptor()
        plain_txt = decryptor.update(encrypted_bytes) + decryptor.finalize()
        # 去掉尾部可能存在的 \x00-\x1F
        return ZERO_RE.sub('', plain_txt.decode('utf-8'))

    def decrypt_b64(self, b64_txt):
        encrypted_bytes = base64.b64decode(b64_txt)
        return self.decrypt(encrypted_bytes)


class Encrypt(object):

    @staticmethod
    def fernet_key() -> bytes:
        key = Fernet.generate_key()
        return key

    def __init__(self, key: str):
        self._factory = Fernet(key.encode())

    def encrypt(self, plain_text: str) -> str:
        return self._factory.encrypt(plain_text.encode()).decode()

    def decrypt(self, cipher_text: str) -> str:
        return self._factory.decrypt(cipher_text.encode()).decode()
    