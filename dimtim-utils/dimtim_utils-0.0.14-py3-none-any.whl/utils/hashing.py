import hashlib
import hmac
from typing import Union


def md5(val: Union[str, bytes]):
    return hashlib.md5(val if isinstance(val, bytes) else str(val).encode()).hexdigest()


def sha1(val: Union[str, bytes]):
    return hashlib.sha1(val if isinstance(val, bytes) else str(val).encode()).hexdigest()


def secret_hmac(key: str, message: str):
    return hmac.digest(key.encode('utf8'), str(message).encode('utf8'), 'sha1').hex()
