# Copyright (c) 2019-2022 Magnusson Institute

from jwcrypto import jwk

from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.serialization import NoEncryption, PrivateFormat, Encoding

def gen_p384_pair(_private_key_ops=['deriveKey', 'sign'], _public_key_ops=['deriveKey', 'verify']):
    """Generates an eliptic curve key in json web key format

    Uses NIST P-384 standard (see `FIPS 186-4`_).

    Args:
        _private_key_ops:  Array of allowed private operations, default is ['deriveKey', 'sign'].
        _public_key_ops:   Array of allowed public operations, default is ['deriveKey', 'verify'].

    Returns:
        Dict: {'private': <private key>, 'public': <public key>}

    .. _FIPS 186-4

       https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.186-4.pdf

    """

    pk = ec.generate_private_key(ec.SECP384R1())
    pk_jwk = jwk.JWK.from_pem(pk.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, NoEncryption()))
    pk_jwk.pop("kid")
    pk_jwk['key_ops'] = _private_key_ops
    pk_jwk['kty'] = 'EC' # sometimes missing for some reason?
    _priv = pk_jwk.export_private()
    pk_jwk['key_ops'] = _public_key_ops
    _pub = pk_jwk.export_public()
    return ({'private':_priv, 'public':_pub})

def gen_aes_key_jwk():
    """Generates a random 256-bit AES encryption key

    Returns:
        JWK format AES key.

    """
    _k = jwk.JWK.generate(kty='oct', size=256)
    _k['alg'] = "A256GCM"  # i think ...
    _k['ext'] = True
    _k['key_ops'] = ["encrypt", "decrypt"]
    return _k.export()

