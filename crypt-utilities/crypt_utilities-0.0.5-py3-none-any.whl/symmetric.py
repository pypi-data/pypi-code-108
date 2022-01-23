
import os
import base64
from pathlib import Path

# ---------------------------------- Symmetric Encryption ----------------------------------
# ------------------------------------------------------------------------------------------
# Fernet is a AES128 algorithm in CBC mode with a SHA256 HMAC message authentication code.
# It is an strong algorithm, see answer to:  
#   https://crypto.stackexchange.com/questions/43120/why-is-fernet-only-aes-128-cbc
# Not necessary to use AES256-GCM in terms of security (both are unbreakable with modern computers)
from cryptography.fernet import Fernet, InvalidToken
# AES256 in GCM mode combines encryption and authentication into the same standard protocol, 
# which can be en/decrypted by browsers (Javascript subtle crypto API) and all other 
# crypto libraries and tools, not just the Python cryptography module.
# The GCM mode is also a lot faster, reaching several gigabytes per second with AES-NI.
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
# ------------------------------------------------------------------------------------------
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

def generate_key() -> bytes:
    return Fernet.generate_key()

def encrypt(data:bytes, key:bytes) -> bytes:
    """Fernet key must be 32 url-safe base64-encoded bytes"""
    fernet = Fernet(key)
    token = fernet.encrypt(data)
    
    return token

def decrypt(token:bytes, key:bytes) -> bytes:
    fernet = Fernet(key)
    decrypted = fernet.decrypt(token)
    
    return decrypted

def encrypt_file(file_path:str, key:bytes, override:bool=True):
    file_path:Path = Path(file_path).resolve()
    with open(file_path, 'rb') as file:
        token = encrypt(file.read(), key)
    if not override:
        file_path = Path(str(file_path.parent/f'encrypted_{file_path.name}'))
    with open(file_path, 'wb') as file: 
        file.write(token)
    
def decrypt_file(file_path:str, key:bytes, override:bool=True):
    file_path:Path = Path(file_path).resolve()
    with open(file_path, 'rb') as file:
        content = decrypt(file.read(), key)
    if not override:
        file_path = Path(str(file_path.parent/f'decrypted_{file_path.name}'))
    with open(file_path, 'wb') as file:
        file.write(content)