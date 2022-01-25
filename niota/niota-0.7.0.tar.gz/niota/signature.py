import base64
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from typing import Union


def load_private_key(pem_private_key: str) -> rsa.RSAPrivateKeyWithSerialization:
    pem_private_key_bytes = pem_private_key.encode('utf-8')
    return serialization.load_pem_private_key(pem_private_key_bytes, password=None)


def load_public_key(pem_public_key: str) -> rsa.RSAPublicKeyWithSerialization:
    pem_public_key_bytes = pem_public_key.encode('utf-8')
    return serialization.load_pem_public_key(pem_public_key_bytes)


def export_private_key(private_key: rsa.RSAPrivateKeyWithSerialization) -> str:
    pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    )
    return pem.decode('utf-8')


def export_public_key(private_key: rsa.RSAPrivateKeyWithSerialization) -> str:
    pem = private_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return pem.decode('utf-8')


def get_pem_public_key(pem_private_key):
    private_key = load_private_key(pem_private_key)
    public_key = private_key.public_key()
    pem_public_key = export_public_key(public_key)
    return pem_public_key


def generate_key_pair():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    return private_key, private_key.public_key()


def sign_message(
    private_key: Union[str, rsa.RSAPrivateKeyWithSerialization],
    message: str
):
    if isinstance(private_key, str):
        private_key = load_private_key(private_key)
    signature = private_key.sign(
        message.encode('utf-8'),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    base64_signature = base64.b64encode(signature).decode('utf-8')
    return base64_signature


def verify_signature(
    public_key: Union[str, rsa.RSAPublicKeyWithSerialization],
    base64_signature: str,
    message: str,
    raise_exception=True,
):
    if isinstance(public_key, str):
        public_key = load_public_key(public_key)
    signature = base64.b64decode(base64_signature.encode('utf-8'))
    try:
        public_key.verify(
            signature,
            message.encode('utf-8'),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
    except InvalidSignature:
        if raise_exception:
            raise
        return False
    else:
        return True
