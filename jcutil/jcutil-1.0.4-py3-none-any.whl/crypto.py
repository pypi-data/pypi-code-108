""" 
A simple aes encrypt and decrypt model with cryptodome
Support modes can check Mode Enum class
"""
# depend on pycryptodomex module
import hashlib
from enum import IntEnum
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad, unpad
import hashlib
from jcramda import curry, enum_value, co, first
from jcramda.base.text import b64_urlsafe_encode

BS = AES.block_size


class Mode(IntEnum):
    EAX = AES.MODE_EAX
    ECB = AES.MODE_ECB
    CBC = AES.MODE_CBC
    OCB = AES.MODE_OCB
    CFB = AES.MODE_CFB
    OFB = AES.MODE_OFB
    CTR = AES.MODE_CTR
    CCM = AES.MODE_CCM
    GCM = AES.MODE_GCM
    SIV = AES.MODE_SIV


@curry
def aes_encrypt(key, plain: str, /, mode=None):
    key = bytes.fromhex(key) if isinstance(key, str) else key
    cipher = AES.new(key, enum_value(mode) or AES.MODE_EAX)
    # add padding to plaintext
    raw = pad(plain.encode(), BS)
    if hasattr(cipher, 'encrypt_and_digest'):
        ciphertext, tag = cipher.encrypt_and_digest(raw)
        nonce_or_iv = getattr(cipher, 'nonce', tag if enum_value(mode) == AES.MODE_SIV else b'')
    else:
        ciphertext = cipher.encrypt(raw)
        nonce_or_iv = getattr(cipher, 'iv', getattr(cipher, 'nonce', b''))
    return tuple(it.hex().upper() for it in (ciphertext, nonce_or_iv))


@curry
def aes_decrypt(key, value: str, /, mode=None, nonce_or_iv: str = None) -> str:
    key = bytes.fromhex(key) if isinstance(key, str) else key
    args = [key, enum_value(mode) or AES.MODE_EAX]
    kws = {}
    if nonce_or_iv:
        if enum_value(mode) == AES.MODE_CTR:
            kws['nonce'] = bytes.fromhex(nonce_or_iv)
        elif enum_value(mode) != AES.MODE_SIV:
            args.append(bytes.fromhex(nonce_or_iv))
    cryptor = AES.new(*args, **kws)
    if enum_value(mode) == AES.MODE_SIV:
        ciphertext = cryptor.decrypt_and_verify(bytes.fromhex(value), bytes.fromhex(nonce_or_iv))
    else:
        ciphertext = cryptor.decrypt(bytes.fromhex(value))
    return unpad(ciphertext, BS).decode()


def get_sha1prng_key(key: str) -> str:
    """[summary]
    encrypt key with SHA1PRNG
    same as java AES crypto key generator SHA1PRNG
    Arguments:
        key {[string]} -- [key]

    Returns:
        [string] -- a 16 bytes key hexstring
    """
    return hashlib.sha1(
        hashlib.sha1(key.encode()).digest()
    ).hexdigest().upper()[:32]

aes_ecb_encrypt = co(first, aes_encrypt(mode=AES.MODE_ECB))
aes_ecb_decrypt = aes_decrypt(mode=AES.MODE_ECB)
aes_cfb_encrypt = aes_encrypt(mode=AES.MODE_CFB)
aes_cfb_decrypt = aes_decrypt(mode=AES.MODE_CFB)


def to_base64(hexstring) -> str:
    return b64_urlsafe_encode(bytes.fromhex(hexstring))


def sha3sum(plaintext) -> str:
    return hashlib.sha3_256(plaintext.encode()).hexdigest().upper()
