import os
import ecdsa
import codecs
import base64
from Crypto.Hash import keccak


def get_address_from_public_key(public_key):
    public_key_bytes = base64.b64decode(public_key)

    hash = keccak.new(digest_bits=256)
    hash.update(public_key_bytes)
    keccak_digest = hash.hexdigest()

    address = '0x' + keccak_digest[-40:]
    return address


def generate_wallet_address():
    private_key_bytes = os.urandom(32)
    keydata = {'public': None, 'private': None, 'address': None}
    key = ecdsa.SigningKey.from_string(
        private_key_bytes, curve=ecdsa.SECP256k1).verifying_key

    key_bytes = key.to_string()

    # the below section is to enable serialization while passing the keys through json
    private_key_final = base64.b64encode(private_key_bytes).decode('utf-8')
    public_key_final = base64.b64encode(key_bytes).decode('utf-8')
    keydata['address'] = get_address_from_public_key(public_key_final)
    keydata['private'] = private_key_final
    keydata['public'] = public_key_final

    return keydata