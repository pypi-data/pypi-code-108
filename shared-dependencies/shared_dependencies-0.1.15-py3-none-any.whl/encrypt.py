import os
import contextlib
import jwt
from jwt.exceptions import PyJWTError, DecodeError, ExpiredSignatureError
import base64
from math import ceil, log
from Crypto.Cipher import AES
from typing import Any
from typing import Dict
from datetime import datetime, timedelta


BLOCK_SIZE = AES.block_size


def pad(s: str) -> str:
    return s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * chr(BLOCK_SIZE - len(s) % BLOCK_SIZE)


def unpad(s: bytes) -> bytes:
    return s[: -ord(s[len(s) - 1 :])]


def encrypt(raw: str, password: str) -> bytes:
    private_key = password.encode("utf-8")
    raw = pad(raw)
    cipher = AES.new(private_key, AES.MODE_ECB)
    return base64.b64encode(cipher.encrypt(raw))


def decrypt(enc: str, password: str) -> bytes:
    private_key = password.encode("utf-8")
    enc_bytes = base64.b64decode(enc)
    cipher = AES.new(private_key, AES.MODE_ECB)
    return unpad(cipher.decrypt(enc_bytes))


def read_key_from_env(key: str, linebreakword: str = "_LINEBREAK_") -> str:
    content = os.getenv(key)
    if content is None:
        raise ValueError(f"{key} not found in env variables")
    if content.startswith(linebreakword):
        content = content[len(linebreakword) :]
    if content.endswith(linebreakword):
        content = content[: -len(linebreakword)]
    return content.replace(linebreakword, "\n")


def decrypt_aes_encoding(token: str, secret: str) -> str:
    try:
        return decrypt(token, secret).decode("utf-8")
    except ValueError:
        raise Exception("Impossible to decode token with given secret")


def ensure_token_validity(token: str) -> None:
    public_key = read_key_from_env("PUBLIC_KEY")
    try:
        payload = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
        )
        if "sub" not in payload:
            raise Exception("sub key is missing")
    except DecodeError:
        raise Exception("token is not an encoded JWT")
    except ExpiredSignatureError:
        raise Exception("token is expired")
    except Exception:
        raise Exception("unknown error")


def get_payload(token: str, safe: bool = True) -> Dict[str, Any]:
    if safe:
        ensure_token_validity(token)
    return jwt.decode(
        token,
        read_key_from_env("PUBLIC_KEY"),
        algorithms=["RS256"],
    )


def nanoid_algorithm(random_bytes: int) -> bytearray:
    """From https://github.com/puyuan/py-nanoid"""
    return bytearray(os.urandom(random_bytes))


def generate_session_id(
    alphabet: str = "_-0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ",
    size: int = 8,
) -> str:
    """Adapted from https://github.com/puyuan/py-nanoid"""
    alphabet_len = len(alphabet)
    mask = 1
    if alphabet_len > 1:
        mask = (2 << int(log(alphabet_len - 1) / log(2))) - 1
    step = int(ceil(1.6 * mask * size / alphabet_len))
    session_id = ""
    while True:
        random_bytes = nanoid_algorithm(step)
        for i in range(step):
            random_byte = random_bytes[i] & mask
            if random_byte < alphabet_len and alphabet[random_byte]:
                session_id += alphabet[random_byte]
                if len(session_id) == size:
                    return session_id


def generate_token(token_info: dict, exp_min: int):
    exp_date = datetime.now() + timedelta(minutes=exp_min)
    exp = {"exp": datetime.timestamp(exp_date)}
    jwt_data = jwt.encode(
        {**token_info, **exp},
        read_key_from_env("PRIVATE_KEY"),
        algorithm="RS256",
    )
    return encrypt(jwt_data, os.getenv("AES_SECRET")).decode("utf-8")


def get_admin_token():
    return generate_token(token_info={"sub": "ms_auth"}, exp_min=15)