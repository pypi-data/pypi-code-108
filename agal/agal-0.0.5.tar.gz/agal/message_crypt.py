import json
import random
import hashlib
import base64
from cryptography.fernet import Fernet, InvalidToken
from . import constant


def gen_key():
    with open('%s/%s' % (constant.LOCATION, 'hamlet.json')) as fd:
        hf_key = '-'.join(random.sample(json.loads(fd.read()), 4))
        return hf_key


def to_b64_key(hf_key):
    b64_key = base64.urlsafe_b64encode(hashlib.sha256(hf_key.encode('utf-8')).digest())
    return b64_key


class MessageCrypt:
    def __init__(self, key):
        self.fernet = Fernet(to_b64_key(key))

    def json_encrypt(self, data):
        data = json.dumps(data).encode('utf-8')
        return self.fernet.encrypt(data)

    def json_decrypt(self, token):
        try:
            if not isinstance(token, bytes):
                token = token.encode('utf-8')
            data = json.loads(self.fernet.decrypt(token))
            return data
        except InvalidToken:
            return None
