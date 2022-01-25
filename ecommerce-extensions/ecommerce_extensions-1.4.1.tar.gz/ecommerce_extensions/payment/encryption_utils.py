""" Module to encrypt the order number in the URL for status page """
import base64

from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from django.conf import settings


def generate_key():
    """ Generate the key for encription
    """
    encryption_key = getattr(settings, 'PAYMENT_ENCRYPTION_KEY', 'encryption_key')
    encryption_key = encryption_key.encode()  # Convert to type bytes
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        iterations=100000,
        salt=getattr(settings, 'PAYMENT_ENCRYPTION_SALT', 'encryption_salt').encode(),
        backend=default_backend(),
    )
    return base64.urlsafe_b64encode(kdf.derive(encryption_key))


def encode_string(message):
    """ Encode the order number
    """
    fernet = Fernet(generate_key())

    return fernet.encrypt(message.encode()).decode("utf-8")


def decode_string(encrypted):
    """ Decode the order number
    """
    fernet = Fernet(generate_key())

    return fernet.decrypt(encrypted.encode()).decode("utf-8")
