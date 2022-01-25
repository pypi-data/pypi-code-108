from Crypto import Random
from Crypto.Cipher import AES
from hashlib import sha256
from base64 import b64encode, b64decode


_BLOCK_SIZE = 16


def _pad(s: str) -> str:
    return (s + (_BLOCK_SIZE - len(s) % _BLOCK_SIZE)
            * chr(_BLOCK_SIZE - len(s) % _BLOCK_SIZE))


def _unpad(s: bytes) -> bytes:
    return s[:-ord(s[len(s) - 1:])]


def aes256_encrypt(data: str, key: str) -> str:
    """
    AES 256-encrypts a string.

    :param data: The data to encrypt
    :param key: Encryption key
    :returns: Encrypted data (base64 encoded)
    """
    private_key = sha256(key.encode('utf8')).digest()
    data = _pad(data)
    iv = Random.new().read(AES.block_size)
    cipher = AES.new(private_key, AES.MODE_CBC, iv)
    return b64encode(
        iv + cipher.encrypt(data.encode('utf8'))).decode('utf8')


def aes256_decrypt(data_encrypted: str, key: str) -> str:
    """
    AES 256-decrypts a string.

    :param data_encrypted: The encrypted data (base64 encoded)
    :param key: Encryption key
    :returns: Decrypted data
    """
    data_encrypted = data_encrypted.encode('utf8')
    private_key = sha256(key.encode('utf8')).digest()
    data_encrypted = b64decode(data_encrypted)
    iv = data_encrypted[:16]
    cipher = AES.new(private_key, AES.MODE_CBC, iv)
    return _unpad(cipher.decrypt(data_encrypted[16:])).decode('utf8')
