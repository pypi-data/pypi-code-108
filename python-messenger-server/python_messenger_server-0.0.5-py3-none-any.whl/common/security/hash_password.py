import hashlib
import binascii
from messenger2.protocols.JIM import JIM


def get_hash_from_password(password, salt):
    """
    get hash from data
    :param password: user password
    :param salt: salt
    :return: string hash password
    """
    hash_pass = hashlib.pbkdf2_hmac(
        "sha256", password=bytes(
            password, encoding=JIM.ENCODING), salt=bytes(
            salt, encoding=JIM.ENCODING), iterations=100000)
    return str(binascii.hexlify(hash_pass), encoding=JIM.ENCODING)
