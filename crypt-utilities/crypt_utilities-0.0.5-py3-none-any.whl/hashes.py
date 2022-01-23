
import os
import base64

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

def generate_salt(length:int=24) -> bytes:
    return os.urandom(length)

def derive(data:bytes, salt:bytes, length:int=32, iterations=400000) -> bytes:
    # pbkdf with secure parameters
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=length,
        salt=salt,
        iterations=iterations,
    )
    # Secure Hash with no collisions thanks to unique salt (must be unique per password)
    salted_hash = kdf.derive(data) 
    # Make the hash url friendly
    salted_hash = base64.urlsafe_b64encode(salted_hash) 
    
    return salted_hash