import base64
import hashlib
from hashlib import md5
from json import loads
from Crypto import Random
from Crypto.Cipher import AES
from ..utils.machineid import MachineID
from ..config import ConfigManager


BLOCK_SIZE = 16

pad = lambda s: str(s) + (BLOCK_SIZE - len(str(s)) % BLOCK_SIZE) * chr(BLOCK_SIZE - len(str(s)) % BLOCK_SIZE)
unpad = lambda s: s[:-ord(s[len(s) - 1:])]
 
def encrypt(raw):
  machineid = MachineID()
  password = machineid.getMachineId()
  private_key = hashlib.sha256(password.encode("utf-8")).digest()
  raw = pad(raw)
  iv = Random.new().read(AES.block_size)
  cipher = AES.new(private_key, AES.MODE_CBC, iv)
  return base64.b64encode(iv + cipher.encrypt(raw.encode()))

 
def decryptFallback(enc, password):
    private_key = hashlib.sha256(password.encode("utf-8")).digest()
    enc = base64.b64decode(enc)
    iv = enc[:16]
    cipher = AES.new(private_key, AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(enc[16:])).decode()

def bytes_to_key(data, salt, output=48):
    assert len(salt) == 8, len(salt)
    data += salt
    key = md5(data).digest()
    final_key = key
    while len(final_key) < output:
        key = md5(key + data).digest()
        final_key += key
    return final_key[:output]

def decryptRemote(encrypted, passphrase):
    encrypted = base64.b64decode(encrypted)
    assert encrypted[0:8] == b"Salted__"
    salt = encrypted[8:16]
    key_iv = bytes_to_key(passphrase, salt, 32+16)
    key = key_iv[:32]
    iv = key_iv[32:]
    aes = AES.new(key, AES.MODE_CBC, iv)
    return unpad(aes.decrypt(encrypted[16:])).decode()

def aesDecryptSecret(secret):
  configManager = ConfigManager()
  config = configManager.getConfig()
  json_data = decryptRemote(secret, config["passcode"].encode())
  json_data = loads(json_data)
  return json_data