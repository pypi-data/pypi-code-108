import base64
import hashlib


def encode_base64(input: bytes, charset: str = "utf-8") -> str:
    """Encode bytes into Base64."""
    file_bytes = base64.encodebytes(input)
    return str(file_bytes, charset)


def calculate_md5(input: bytes) -> str:
    """Calculate an MD5 hash from bytes."""
    return hashlib.md5(input).hexdigest()
