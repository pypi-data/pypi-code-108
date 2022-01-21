from abc import ABC, abstractmethod


class BushBP(ABC):
    @abstractmethod
    def __init__(self, key: bytes) -> None:
        pass

    def encrypt(self, data: bytes) -> bytes:
        pass

    def decrypt(self, data: bytes) -> bytes:
        pass

    def __encryptor(self, key: bytes, data: bytes) -> bytes:
        pass

    def __decryptor(self, data: bytes) -> bytes:
        pass

    @classmethod
    def generate_key(cls) -> bytes:
        pass

    @staticmethod
    def __padder(data: bytes) -> bytes:
        pass

    @staticmethod
    def __unpadder(data: bytes) -> bytes:
        pass

    @staticmethod
    def __finalize(signed_data: bytes, cipher_text: bytes, iv: bytes) -> bytes:
        pass

    @staticmethod
    def __check_signature(data: bytes, prev_key: bytes, key: bytes):
        pass
