# Copyright 2016 to 2021, Cisco Systems, Inc., all rights reserved.
import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def encrypt_plaintext(plaintext, password):
    """Encrypt the given plaintext.

    .. seealso::
      https://cryptography.io/en/latest/fernet/#using-passwords-with-fernet

    Args:
      plaintext (str): Plaintext to encrypt, as unicode string
      password (str): Password used to encrypt the plaintext for recovery,
        as unicode string

    Returns:
      str: ``<base64 salt>$<base64 ciphertext>`` as unicode string
    """
    if not plaintext:
        return u''
    # Convert password to a 32-byte base64 string
    salt = os.urandom(16)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode('utf-8')))

    f = Fernet(key)
    token = f.encrypt(plaintext.encode('utf-8'))

    return (base64.urlsafe_b64encode(salt) + b'$' + token).decode('utf-8')


def decrypt_ciphertext(ciphertext, password):
    """Inverse of :func:`encrypt_plaintext`.

    Args:
      ciphertext (str): ``<base64 salt>$<base64 ciphertext>`` (unicode)
      password (str): Password (unicode) used to decrypt the ciphertext

    Returns:
      str: Decrypted plaintext (unicode)
    """
    if not ciphertext:
        return u''
    if b'$' not in ciphertext.encode('utf-8'):
        raise ValueError('String is not in the form "salt$ciphertext"')
    salt64, ciphertext64 = ciphertext.encode('utf-8').split(b'$', 1)
    salt = base64.urlsafe_b64decode(salt64)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode('utf-8')))

    f = Fernet(key)
    plaintext = f.decrypt(ciphertext64)

    return plaintext.decode('utf-8')
