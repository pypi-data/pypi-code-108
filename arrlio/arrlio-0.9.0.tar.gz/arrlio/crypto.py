import os

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import padding as symmetric_padding
from cryptography.hazmat.primitives.asymmetric import padding as asymmetric_padding
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


AES_BLOCK_SIZE = algorithms.AES.block_size


def s_encrypt(data: bytes, key: bytes) -> bytes:
    if len(key) < 16:
        key += b" " * (16 - len(key))
    iv = os.urandom(16)
    padder = symmetric_padding.PKCS7(AES_BLOCK_SIZE).padder()
    bitstring = padder.update(data) + padder.finalize()
    cipher = Cipher(algorithms.AES(key[0:16]), modes.CBC(iv))
    encryptor = cipher.encryptor()
    return iv + (encryptor.update(bitstring) + encryptor.finalize())


def s_decrypt(data: bytes, key: bytes) -> bytes:
    if len(key) < 16:
        key += b" " * (16 - len(key))
    iv = data[0:16]
    cipher = Cipher(algorithms.AES(key[0:16]), modes.CBC(iv))
    decryptor = cipher.decryptor()
    bitstring = decryptor.update(data[16:]) + decryptor.finalize()
    unpadder = symmetric_padding.PKCS7(AES_BLOCK_SIZE).unpadder()
    return unpadder.update(bitstring) + unpadder.finalize()


def generate_crypto_key(length: int = 32) -> bytes:
    return os.urandom(length)


def generate_private_key() -> RSAPrivateKey:
    return rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())


def a_encrypt(data: bytes, public_key: RSAPublicKey) -> bytes:
    return b"".join(
        public_key.encrypt(
            # fmt: off
            data[i: i + 190],
            # fmt: on
            asymmetric_padding.OAEP(
                mgf=asymmetric_padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )
        for i in range(0, len(data), 190)
    )


def a_decrypt(data: bytes, private_key: RSAPrivateKey) -> bytes:
    return b"".join(
        private_key.decrypt(
            # fmt: off
            data[i: i + 256],
            # fmt: on
            asymmetric_padding.OAEP(
                mgf=asymmetric_padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )
        for i in range(0, len(data), 256)
    )
