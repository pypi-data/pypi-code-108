import base64
import functools
import operator
import time
import typing
import fastapi
import orjson
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from starlette import status
from dataclasses import dataclass
from token_proto import Token as _Token
from .config import config

with open(config.public_key, "br") as f:
    public_key = serialization.load_pem_public_key(f.read())

_token = _Token()


@dataclass
class Token:
    user_id: int
    project_id: int
    methods: typing.Union[typing.List[str], str]
    exp: float

    @classmethod
    def from_proto(cls, data: bytes):
        token = _Token.FromString(data)
        # ret = token.SerializeToDict()
        return cls(
            user_id=token.user_id,
            project_id=token.project_id,
            methods=token.methods,
            exp=token.exp,
        )

    def to_proto(self, encode=False):
        ret = _Token()
        ret.user_id = self.user_id
        ret.project_id = self.project_id
        ret.methods = self.methods
        ret.exp = self.exp
        if encode:
            return base64.b64encode(ret.SerializeToString())
        else:
            return ret.SerializeToString()

    def to_json(self):
        ret = orjson.dumps(self)
        return ret

    def to_m(self):
        m = self.methods.encode()
        ret = (
            self.user_id.to_bytes(4, "big", signed=False),
            self.project_id.to_bytes(4, "big", signed=False),
            int(self.exp).to_bytes(4, "big", signed=False),
            len(m).to_bytes(1, "big", signed=False),
            m,
        )
        return functools.reduce(operator.add, ret)

    @classmethod
    def from_json(cls, v):
        ret = orjson.loads(v)
        return cls(
            **{
                "user_id": ret["user_id"],
                "project_id": ret["project_id"],
                "methods": ret["methods"],
                "exp": ret["exp"],
            }
        )


def verify_b64_token(data: str, method: str):
    return verify_token(base64.b64decode(data), method)


def verify_token(data: bytes, method: str):
    """
    Проверяет подпись, сверяет id проекта, запрошенный метод и срок валидности
    :param data:
    :param method:
    :return:
    """
    sig = data[:256]
    token = data[256:]
    ex = fastapi.HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    try:
        public_key.verify(
            sig,
            token,
        )
        token = Token.from_proto(token)
        if (
            token.project_id != config.project_id
            or method not in token.methods
            or token.exp < time.time()
        ):
            raise ex
        return token
    except InvalidSignature:
        raise ex
