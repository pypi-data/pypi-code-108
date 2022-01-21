#!/usr/bin/env python
# -*- coding:utf-8 -*-
import time
import jwt
from jwt.exceptions import (
    DecodeError,
    ExpiredSignatureError,
    ImmatureSignatureError,
    InvalidAudienceError,
    InvalidIssuedAtError,
    InvalidIssuerError,
    MissingRequiredClaimError,
)
HS256 = "HS256"
default_headers = {"alg": HS256}

class JwtToken(object):

    def __init__(self, message, secret, exp=3600, algorithm=None, headers=None):
        self.secret = secret    # key
        self.exp = exp
        self.payload = {"message": message}
        self.algorithm = algorithm or HS256
        self.headers = headers or default_headers

    def get_token(self):
        return self.encode()

    def encode(self):
        return jwt.encode(self._get_playload(self.payload), self.secret, self.algorithm, self.headers)

    def decode(self, token):
        return jwt.decode(token, self.secret, self.algorithm)

    def is_expire(self, token):
        try:
            self.decode(token)
        except ExpiredSignatureError as e:
            return True
        else:
            return False

    def is_validate(self, token):
        try:
            payload = jwt.decode(token, self.secret, self.algorithm)
            return True
        except Exception as e:
            return False

    def refresh_token(self, token):
        try:
            self.payload = self.decode(token)
            return self.encode()
        except Exception as e:
            return False

    def _get_playload(self, payload):
        assert isinstance(payload, dict)

        expire_time = int(time.time()) + self.exp
        payload.update({"exp": expire_time})

        return payload

if __name__ == '__main__':
    t = JwtToken(54887111, "f465ca164f0e", 3600)
    token = t.encode()
    print(token)
    message, exp = t.decode(token).values()
    print(message, exp)

    print(t.is_expire(token))
    print(t.is_validate(token))
    print(t.refresh_token(token))