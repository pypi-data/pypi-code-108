"""
Provides cryptographic methods for device provisioning and authentication.

The files ODrivePrivate/tools/odrive/crypto.py and
ODriveInfrastructure/lib/crypto.py are identical should be kept in sync.

The following algorithms and encodings are used:

Signature algorithm: NIST P-256 (aka SECP256R1)
Hashing algorithm: SHA-256

Private key: 32 bytes private value (big endian)
Public key: 32 bytes X coordinate (big endian) + 32 bytes Y coordinate (big endian)
Signature: 32 bytes R (big endian) + 32 bytes S (big endian)

These match the algorithms/encodings on the ATECCx08 chips found on ODrive
hardware and must therefore not be changed.
"""

# TODO: this is a non-standard python module. Try to get rid of it.
# May implement these functions without external library:
# https://onyb.gitbook.io/secp256k1-python/ecdsa
import cryptography.exceptions
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import base64

InvalidSignature = cryptography.exceptions.InvalidSignature

def gen_key() -> ec.EllipticCurvePrivateKey:
    """
    Creates a new private key. The public key can be derived from this.
    """
    return ec.generate_private_key(ec.SECP256R1(), default_backend())

def get_private_bytes(private_key: ec.EllipticCurvePrivateKey) -> bytes:
    """
    Returns the raw byte representation of `private_key`.
    See file header for encoding details.
    """
    return ec.utils.int_to_bytes(private_key.private_numbers().private_value, 32)

def get_public_bytes(public_key: ec.EllipticCurvePublicKey) -> bytes:
    """
    Returns the raw byte representation of `public_key`.
    See file header for encoding details.
    """
    public_numbers = public_key.public_numbers()
    return ec.utils.int_to_bytes(public_numbers.x, 32) + ec.utils.int_to_bytes(public_numbers.y, 32)

def load_private_key(private_bytes: bytes) -> ec.EllipticCurvePrivateKey:
    """
    Loads a private key object from the raw representation in `private_bytes`.
    See file header for encoding details.
    """
    assert len(private_bytes) == 32
    private_value = int.from_bytes(private_bytes, 'big')
    return ec.derive_private_key(private_value, ec.SECP256R1(), default_backend())

def load_public_key(public_bytes: bytes) -> ec.EllipticCurvePublicKey:
    """
    Loads a public key object from the raw representation in `public_bytes`.
    See file header for encoding details.
    """
    assert len(public_bytes) == 64
    x_int = int.from_bytes(public_bytes[:32], 'big')
    y_int = int.from_bytes(public_bytes[32:], 'big')
    return ec.EllipticCurvePublicNumbers(x_int, y_int, ec.SECP256R1()).public_key(default_backend())

def sign(private_key: ec.EllipticCurvePrivateKey, data: bytes) -> bytes:
    """
    Hashes `data` and signs the resulting digest using `private_key`.
    See file header for algorithm and encoding details.
    """
    der_signature = private_key.sign(data, ec.ECDSA(hashes.SHA256()))

    # Convert signature from DER format to raw 64 byte encoding
    assert (der_signature[0] == 48) and (der_signature[1] == len(der_signature) - 2)
    def from_der(buf):
        assert buf[0] == 2, buf[0]
        num = ec.utils.int_to_bytes(int.from_bytes(buf[2:][:buf[1]], 'big'), 32)
        return num, buf[buf[1]+2:]
    r_buf, der_signature = from_der(der_signature[2:])
    s_buf, der_signature = from_der(der_signature)
    assert der_signature == b''

    return r_buf + s_buf

def verify(public_key: ec.EllipticCurvePublicKey, signature: bytes, data: bytes):
    """
    Verifies a signature obtained with `sign()`.
    See file header for algorithm and encoding details.
    """
    assert len(signature) == 64

    # Convert signature from raw 64 byte encoding to ASN1 DER encoding
    def to_der(buf):
        buf = ec.utils.int_to_bytes(int.from_bytes(buf, 'big'))
        return (b'\0' if (buf[0] & 0x80) else b'') + buf
    r_buf = to_der(signature[:32])
    s_buf = to_der(signature[32:])
    der_signature = [48, len(r_buf) + len(s_buf) + 4, 2, len(r_buf), *r_buf, 2, len(s_buf), *s_buf]

    public_key.verify(der_signature, data, ec.ECDSA(hashes.SHA256()))

def verify_cert(certificate: bytes, device_public_key: ec.EllipticCurvePublicKey, test_mode: bool = False):
    """
    Verifies the device certificate cryptographically against the ODrive master
    key.
    Format of `certificate` documented at ../README.md#device-certificate
    """
    assert len(certificate) == 272, len(certificate)

    message = certificate[:80] + get_public_bytes(device_public_key)
    verify(load_public_key(certificate[144:208]), certificate[80:144], message)

    message = b'ODrive batch key'.ljust(32, b'\0') + certificate[144:208]
    verify(test_master_key if test_mode else master_key, certificate[208:272], message)

def b64encode(buf: bytes) -> str:
    return base64.b64encode(buf).decode('utf-8')

def b64decode(buf: str) -> bytes:
    return base64.b64decode(buf.encode('utf-8'))

master_key = load_public_key(bytes([
    0x60, 0xea, 0x3e, 0x6d, 0xc1, 0x18, 0xa2, 0x1f,
    0x3a, 0x61, 0x99, 0x0c, 0x61, 0x6e, 0xe4, 0x4a,
    0x02, 0x68, 0x80, 0xa2, 0x5c, 0x70, 0x21, 0xac,
    0x6c, 0x63, 0x0b, 0x75, 0x39, 0x9b, 0x1b, 0xe2,
    0x7c, 0xd1, 0x34, 0xc5, 0xd4, 0xf2, 0xa9, 0x1e,
    0x0b, 0x23, 0x3a, 0x18, 0xb6, 0x43, 0xd5, 0x49,
    0x7a, 0xd9, 0xe9, 0x3b, 0x8a, 0x52, 0xfe, 0x92,
    0x95, 0x06, 0xcd, 0x46, 0x18, 0xcf, 0x4c, 0x59
]))

test_master_key_private = load_private_key(bytes([
    0xa9, 0x6a, 0x76, 0xd7, 0x54, 0x53, 0x2e, 0x2a,
    0x38, 0x7a, 0xc5, 0x54, 0x16, 0x53, 0x70, 0xf3,
    0x48, 0x84, 0x9a, 0xf1, 0x82, 0x11, 0xbf, 0xd2,
    0x1f, 0x3c, 0x05, 0xf7, 0xf3, 0xeb, 0xef, 0x08
]))

test_master_key = test_master_key_private.public_key()
