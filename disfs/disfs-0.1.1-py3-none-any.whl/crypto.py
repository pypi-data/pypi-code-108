from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto import Random
from base64 import b64decode, b64encode

def new_key():
    return Random.new().read(32)

def sha256hash(data, string=False):
    if string:
        data = data.encode("utf-8")
    
    return SHA256.new(data).digest()

def encrypt(key, source, string=False):
    if string:
        source = source.encode("utf-8")
    
    IV = Random.new().read(AES.block_size)
    encryptor = AES.new(key, AES.MODE_CBC, IV)
    padding = AES.block_size - len(source) % AES.block_size
    source += bytes([padding]) * padding
    data = IV + encryptor.encrypt(source)
    
    if string:
        return b64encode(data).decode("utf-8")
    else:
        return data

def decrypt(key, source, string=False):
    if string:
        source = b64decode(source)
    
    IV = source[:AES.block_size]
    decryptor = AES.new(key, AES.MODE_CBC, IV)
    data = decryptor.decrypt(source[AES.block_size:])
    padding = data[-1]
    
    if data[-padding:] != bytes([padding]) * padding:
        raise ValueError("Invalid padding")
    
    if string:
        return data[:-padding].decode("utf-8")
    else:
        return data[:-padding]
