"""Bmbix API for AI agents"""

from base64 import b64encode
from datetime import datetime
import hashlib
import logging
import os
from typing import Tuple

import attr
from cryptography.hazmat.primitives.asymmetric import (
    padding,
    rsa,
)

from cryptography.hazmat.primitives import (
    hashes,
    serialization,
)
from dateparser import parse  # type: ignore
from Crypto.Cipher import AES  # type: ignore

from bmb_martlet_organization_client import (  # type: ignore
    ApiClient,
    EncryptionApi,
    PublicKey as PublicKeyGW,
)


logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


@attr.s
class ResourcePublicKey:
    fingerprint: str = attr.ib(default=None)
    public_key: rsa.RSAPublicKey = attr.ib(default=None)
    expires_at: datetime = attr.ib(default=None)
    bri: str = attr.ib(default=None)


def adapt(
    pk: PublicKeyGW,
) -> ResourcePublicKey:
    fingerprint = pk.fingerprint
    bri = pk.uri
    public_key = serialization.load_pem_public_key(pk.data.encode("utf-8"))
    expires_at = parse(pk.expires_at)
    resource_public_key: ResourcePublicKey = ResourcePublicKey(
        fingerprint=fingerprint,
        public_key=public_key,  # type: ignore
        expires_at=expires_at,
        bri=bri,
    )
    return resource_public_key


def generate_fingerprint(
    public_key: rsa.RSAPublicKey,
) -> str:
    modulus: int = public_key.public_numbers().n
    modulus_s: str = str(modulus)
    modulus_b: bytes = bytes(modulus_s, "utf-8")
    hash = hashlib.sha256(modulus_b)
    return hash.hexdigest()


def generate_symmetric_key(
    length: int = 32,
) -> bytes:
    return os.urandom(length)


def encrypt_aes(
        plaintext: bytes,
        key: bytes,
) -> Tuple[bytes, bytes, bytes]:
    cipher = AES.new(key, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(plaintext)
    nonce: bytes = cipher.nonce
    return nonce, ciphertext, tag


def pack_rubric(
    algorithm: bytes,
    key: bytes,
    nonce: bytes,
    tag: bytes,
) -> bytes:
    algorithm_ = b64encode(algorithm).decode("utf-8")
    key_ = b64encode(key).decode("utf-8")
    nonce_ = b64encode(nonce).decode("utf-8")
    tag_ = b64encode(tag).decode("utf-8")
    rubric = f"{algorithm_}:{key_}:{nonce_}:{tag_}"
    rubric_ = bytes(rubric, "utf-8")
    return rubric_


def encrypt_rubric(
    public_key: rsa.RSAPublicKey,
    rubric_plaintext: bytes,
) -> bytes:
    rubric_ciphertext: bytes = public_key.encrypt(
        rubric_plaintext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )
    return rubric_ciphertext


def bmbix_fetch_public_key(
    api_client: ApiClient,
    resource_type: str,
    resource_id: str,
) -> ResourcePublicKey:

    api = EncryptionApi(api_client)
    public_key_response_gw = api.get_resource_public_key(
        resource_type,
        resource_id,
    )
    public_key_gw = public_key_response_gw.public_key
    resource_public_key: ResourcePublicKey = adapt(public_key_gw)
    return resource_public_key
