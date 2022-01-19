from .crypto import encrypt, decrypt, sha256hash
from .discord import Discord
from getpass import getuser, getpass
from keyring import set_password, get_password
from binascii import hexlify
from random import choices
from json import loads, dumps
from config_path import ConfigPath

AUTH_FILE = ConfigPath("disfs", "auth", ".txt").saveFilePath(mkdir=True)

def get_master_key():
    return sha256hash(get_password("raics", getuser()), string=True)

def set_master_key():
    set_password("raics", getuser(), getpass())

def set_client(token, channel, listing):
    auth_data = {"token": token, "channel": channel, "listing": listing}
    
    with open(AUTH_FILE, "w") as f:
        f.write(encrypt(get_master_key(), dumps(auth_data), string=True))

def get_client():
    with open(AUTH_FILE, "r") as f:
        auth_data = loads(decrypt(get_master_key(), f.read(), string=True))
    
    client = Discord()
    client.login(auth_data["token"], auth_data["channel"], auth_data["listing"])
    
    return client
