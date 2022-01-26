import rsa
import base64
import typing

from Crypto.PublicKey import RSA
from .strutils import smart_get_binary_data


def newkeys(nbits=2048):
    """Generate a new RSA key pair.

    In [1]: from fastutils import rsautils

    In [2]: rsautils.newkeys()
    Out[2]:
    (RsaKey(n=1234...7891, e=65537), RsaKey(n=1234...7891, e=65537, d=2345...6789, p=3456...9087, q=4567..9876, u=6789...1234))
    
    """
    sk = RSA.generate(nbits)
    pk = sk.publickey()
    return pk, sk

def load_private_key(text, passphrase=None):
    """Load private key from PEM string.
    """
    sk = RSA.import_key(text, passphrase=passphrase)
    return sk

def load_public_key(text):
    """Load public key from PEM string.
    """
    pk = RSA.import_key(text)
    return pk

def load_public_key_from_private_key(text, passphrase=None):
    """Get public key from private key.
    """
    sk = load_private_key(text, passphrase)
    pk = sk.publickey()
    return pk

def encrypt(data: bytes, pk: typing.Union[RSA.RsaKey, rsa.PublicKey]):
    """Use public key to encrypt the data, so that only the owner of the private key can decrypt the data.
    """
    if isinstance(data, str):
        data = data.encode("utf-8")
    if isinstance(pk, RSA.RsaKey):
        pk = rsa.PublicKey(pk.n, pk.e)
    encrypted_data = rsa.encrypt(data, pk)
    return "".join(base64.encodebytes(encrypted_data).decode().splitlines())

def decrypt(data: str, sk: typing.Union[RSA.RsaKey, rsa.PrivateKey]):
    """Use private key to decrypt the data that encrypted with the public key.
    """
    if isinstance(sk, RSA.RsaKey):
        sk = rsa.PrivateKey(sk.n, sk.e, sk.d, sk.p, sk.q)
    encrypted_data = smart_get_binary_data(data)
    data = rsa.decrypt(encrypted_data, sk)
    return data

def export_key(rsakey: typing.Union[RSA.RsaKey, rsa.PublicKey, rsa.PrivateKey]):
    """Export the private key or the public key to PEM string.
    """
    if isinstance(rsakey, rsa.PublicKey):
        rsakey = RSA.RsaKey(n=rsakey.n, e=rsakey.e)
    elif isinstance(rsakey, rsa.PrivateKey):
        rsakey = RSA.RsaKey(n=rsakey.n, e=rsakey.e, d=rsakey.d, p=rsakey.p, q=rsakey.q)
    return rsakey.export_key().decode()
