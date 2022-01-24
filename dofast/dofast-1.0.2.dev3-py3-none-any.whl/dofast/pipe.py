'''pipe file to connect core files and application files'''
import os
from typing import Dict, List, Optional, Tuple, Union

import codefast as cf
import joblib

from .authorization import Authorization
from cryptography.fernet import Fernet
import base64
import json
from getpass import getpass


class AccountLoader:
    __db = os.path.join(cf.io.dirname(), 'memory.joblib')
    __keys = ['host', 'port', 'password', 'fernet_key']

    @classmethod
    def decode_config_file(cls) -> dict:
        loc = os.path.join(cf.io.dirname(), 'data/redis.txt')
        text = cf.io.reads(loc).encode()
        passwd = getpass('Enter password: ').rstrip()
        passwd = base64.urlsafe_b64encode(passwd.encode() * 10)
        key = Fernet.generate_key()
        key = passwd.decode('utf-8')[:43] + key.decode('utf-8')[43:]
        f = Fernet(key.encode())
        return json.loads(f.decrypt(text).decode('utf-8'))

    @classmethod
    def query_secrets(cls) -> Tuple[str]:
        try:
            list_ = joblib.load(cls.__db)
            list_[-1] = bytes(list_[-1], 'utf-8')
            return tuple(list_)
        except Exception as e:
            cf.error('joblib loading file error: ', e)
            return None

    @classmethod
    def set_secrets(cls, secrets: Dict[str, str]) -> None:
        values = [secrets[k] for k in cls.__keys]
        joblib.dump(values, cls.__db)

    @classmethod
    def init_auth(cls) -> Authorization:
        secrets = cls.query_secrets()
        if secrets:
            return Authorization(secrets[0], secrets[1], secrets[2],
                                 secrets[3])

        accounts = cls.decode_config_file()
        cls.set_secrets(accounts)
        host, port, password, fernet_key = cls.query_secrets()
        return Authorization(host, port, password, fernet_key)


author = AccountLoader.init_auth()
