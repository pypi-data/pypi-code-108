# Make coding more python3-ish


__metaclass__ = type


class AXC2Error(Exception):
    pass


class AXC2VaultError(Exception):
    pass


# ------------------------------------------------------ ansible/parsing/vault:
# FIXME: ansible is GPL3, not sure if this is public domain knowhow or not
# Maybe factorize these 100 lines?
import os
import warnings
from binascii import hexlify, unhexlify

HAS_CRYPTOGRAPHY = False
HAS_PYCRYPTO = False
HAS_SOME_PYCRYPTO = False
CRYPTOGRAPHY_BACKEND = None
try:
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', DeprecationWarning)
        from cryptography.exceptions import InvalidSignature
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import hashes, padding
    from cryptography.hazmat.primitives.hmac import HMAC
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives.ciphers import (
        Cipher as C_Cipher,
        algorithms,
        modes,
    )

    CRYPTOGRAPHY_BACKEND = default_backend()
    HAS_CRYPTOGRAPHY = True
except ImportError:
    pass

try:
    from Crypto.Cipher import AES as AES_pycrypto

    HAS_SOME_PYCRYPTO = True

    # Note: Only used for loading obsolete VaultAES files.  All files are written
    # using the newer AES256Vault which does not require md5
    from Crypto.Hash import SHA256 as SHA256_pycrypto
    from Crypto.Hash import HMAC as HMAC_pycrypto

    # Counter import fails for 2.0.1, requires >= 2.6.1 from pip
    from Crypto.Util import Counter as Counter_pycrypto

    # KDF import fails for 2.0.1, requires >= 2.6.1 from pip
    from Crypto.Protocol.KDF import PBKDF2 as PBKDF2_pycrypto

    HAS_PYCRYPTO = True
except ImportError:
    pass


class AES256Vault:

    """
    Vault implementation using AES-CTR with an HMAC-SHA256 authentication code.
    Keys are derived using PBKDF2
    """

    # http://www.daemonology.net/blog/2009-06-11-cryptographic-right-answers.html

    # Note: strings in this class should be byte strings by default.

    def __init__(self):
        if not HAS_CRYPTOGRAPHY and not HAS_PYCRYPTO:
            raise AXC2Error(NEED_CRYPTO_LIBRARY)

    @staticmethod
    def _create_key_cryptography(b_password, b_salt, key_length, iv_length):
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=2 * key_length + iv_length,
            salt=b_salt,
            iterations=10000,
            backend=CRYPTOGRAPHY_BACKEND,
        )
        b_derivedkey = kdf.derive(b_password)

        return b_derivedkey

    @staticmethod
    def _pbkdf2_prf(p, s):
        hash_function = SHA256_pycrypto
        return HMAC_pycrypto.new(p, s, hash_function).digest()

    @classmethod
    def _create_key_pycrypto(cls, b_password, b_salt, key_length, iv_length):

        # make two keys and one iv

        b_derivedkey = PBKDF2_pycrypto(
            b_password,
            b_salt,
            dkLen=(2 * key_length) + iv_length,
            count=10000,
            prf=cls._pbkdf2_prf,
        )
        return b_derivedkey

    @classmethod
    def _gen_key_initctr(cls, b_password, b_salt):
        # 16 for AES 128, 32 for AES256
        key_length = 32

        if HAS_CRYPTOGRAPHY:
            # AES is a 128-bit block cipher, so IVs and counter nonces are 16 bytes
            iv_length = algorithms.AES.block_size // 8

            b_derivedkey = cls._create_key_cryptography(
                b_password, b_salt, key_length, iv_length
            )
            b_iv = b_derivedkey[(key_length * 2) : (key_length * 2) + iv_length]
        elif HAS_PYCRYPTO:
            # match the size used for counter.new to avoid extra work
            iv_length = 16

            b_derivedkey = cls._create_key_pycrypto(
                b_password, b_salt, key_length, iv_length
            )
            b_iv = hexlify(
                b_derivedkey[(key_length * 2) : (key_length * 2) + iv_length]
            )
        else:
            raise AXC2Error(NEED_CRYPTO_LIBRARY + '(Detected in initctr)')

        b_key1 = b_derivedkey[:key_length]
        b_key2 = b_derivedkey[key_length : (key_length * 2)]

        return b_key1, b_key2, b_iv

    @staticmethod
    def _encrypt_cryptography(b_plaintext, b_key1, b_key2, b_iv):
        cipher = C_Cipher(algorithms.AES(b_key1), modes.CTR(b_iv), CRYPTOGRAPHY_BACKEND)
        encryptor = cipher.encryptor()
        padder = padding.PKCS7(algorithms.AES.block_size).padder()
        b_ciphertext = encryptor.update(padder.update(b_plaintext) + padder.finalize())
        b_ciphertext += encryptor.finalize()

        # COMBINE SALT, DIGEST AND DATA
        hmac = HMAC(b_key2, hashes.SHA256(), CRYPTOGRAPHY_BACKEND)
        hmac.update(b_ciphertext)
        b_hmac = hmac.finalize()

        return (
            to_bytes(hexlify(b_hmac), errors='surrogate_or_strict'),
            hexlify(b_ciphertext),
        )

    @staticmethod
    def _encrypt_pycrypto(b_plaintext, b_key1, b_key2, b_iv):
        # PKCS#7 PAD DATA http://tools.ietf.org/html/rfc5652#section-6.3
        bs = AES_pycrypto.block_size
        padding_length = (bs - len(b_plaintext) % bs) or bs
        b_plaintext += to_bytes(
            padding_length * chr(padding_length), encoding='ascii', errors='strict'
        )

        # COUNTER.new PARAMETERS
        # 1) nbits (integer) - Length of the counter, in bits.
        # 2) initial_value (integer) - initial value of the counter. "iv" from _gen_key_initctr

        ctr = Counter_pycrypto.new(128, initial_value=int(b_iv, 16))

        # AES.new PARAMETERS
        # 1) AES key, must be either 16, 24, or 32 bytes long -- "key" from _gen_key_initctr
        # 2) MODE_CTR, is the recommended mode
        # 3) counter=<CounterObject>

        cipher = AES_pycrypto.new(b_key1, AES_pycrypto.MODE_CTR, counter=ctr)

        # ENCRYPT PADDED DATA
        b_ciphertext = cipher.encrypt(b_plaintext)

        # COMBINE SALT, DIGEST AND DATA
        hmac = HMAC_pycrypto.new(b_key2, b_ciphertext, SHA256_pycrypto)

        return (
            to_bytes(hmac.hexdigest(), errors='surrogate_or_strict'),
            hexlify(b_ciphertext),
        )

    @classmethod
    def encrypt(cls, b_plaintext, secret):
        if secret is None:
            raise AXC2VaultError('The secret passed to encrypt() was None')
        b_salt = os.urandom(32)
        # b_password = secret.bytes
        b_password = secret
        b_key1, b_key2, b_iv = cls._gen_key_initctr(b_password, b_salt)

        if HAS_CRYPTOGRAPHY:
            b_hmac, b_ciphertext = cls._encrypt_cryptography(
                b_plaintext, b_key1, b_key2, b_iv
            )
        elif HAS_PYCRYPTO:
            b_hmac, b_ciphertext = cls._encrypt_pycrypto(
                b_plaintext, b_key1, b_key2, b_iv
            )
        else:
            raise AXC2Error(NEED_CRYPTO_LIBRARY + '(Detected in encrypt)')

        b_vaulttext = b'\n'.join([hexlify(b_salt), b_hmac, b_ciphertext])
        # Unnecessary but getting rid of it is a backwards incompatible vault
        # format change
        b_vaulttext = hexlify(b_vaulttext)
        return b_vaulttext

    @classmethod
    def _decrypt_cryptography(cls, b_ciphertext, b_crypted_hmac, b_key1, b_key2, b_iv):
        # b_key1, b_key2, b_iv = self._gen_key_initctr(b_password, b_salt)
        # EXIT EARLY IF DIGEST DOESN'T MATCH
        hmac = HMAC(b_key2, hashes.SHA256(), CRYPTOGRAPHY_BACKEND)
        hmac.update(b_ciphertext)
        try:
            hmac.verify(unhexlify(b_crypted_hmac))
        except InvalidSignature as e:
            raise AXC2VaultError('HMAC verification failed: %s' % e)

        cipher = C_Cipher(algorithms.AES(b_key1), modes.CTR(b_iv), CRYPTOGRAPHY_BACKEND)
        decryptor = cipher.decryptor()
        unpadder = padding.PKCS7(128).unpadder()
        b_plaintext = (
            unpadder.update(decryptor.update(b_ciphertext) + decryptor.finalize())
            + unpadder.finalize()
        )

        return b_plaintext

    @staticmethod
    def _is_equal(b_a, b_b):
        """
        Comparing 2 byte arrrays in constant time
        to avoid timing attacks.

        It would be nice if there was a library for this but
        hey.
        """
        if not (isinstance(b_a, binary_type) and isinstance(b_b, binary_type)):
            raise TypeError('_is_equal can only be used to compare two byte strings')

        # http://codahale.com/a-lesson-in-timing-attacks/
        if len(b_a) != len(b_b):
            return False

        result = 0
        for b_x, b_y in zip(b_a, b_b):
            if PY3:
                result |= b_x ^ b_y
            else:
                result |= ord(b_x) ^ ord(b_y)
        return result == 0

    @classmethod
    def _decrypt_pycrypto(cls, b_ciphertext, b_crypted_hmac, b_key1, b_key2, b_iv):
        # EXIT EARLY IF DIGEST DOESN'T MATCH
        hmac_decrypt = HMAC_pycrypto.new(b_key2, b_ciphertext, SHA256_pycrypto)
        if not cls._is_equal(b_crypted_hmac, to_bytes(hmac_decrypt.hexdigest())):
            return None

        # SET THE COUNTER AND THE CIPHER
        ctr = Counter_pycrypto.new(128, initial_value=int(b_iv, 16))
        cipher = AES_pycrypto.new(b_key1, AES_pycrypto.MODE_CTR, counter=ctr)

        # DECRYPT PADDED DATA
        b_plaintext = cipher.decrypt(b_ciphertext)

        # UNPAD DATA
        if PY3:
            padding_length = b_plaintext[-1]
        else:
            padding_length = ord(b_plaintext[-1])

        b_plaintext = b_plaintext[:-padding_length]
        return b_plaintext

    @classmethod
    def decrypt(cls, b_vaulttext, secret):
        # SPLIT SALT, DIGEST, AND DATA
        b_vaulttext = unhexlify(b_vaulttext)
        b_salt, b_crypted_hmac, b_ciphertext = b_vaulttext.split(b'\n', 2)
        b_salt = unhexlify(b_salt)
        b_ciphertext = unhexlify(b_ciphertext)

        # TODO: would be nice if a VaultSecret could be passed directly to _decrypt_*
        #       (move _gen_key_initctr() to a AES256 VaultSecret or VaultContext impl?)
        # though, likely needs to be python cryptography specific impl that basically
        # creates a Cipher() with b_key1, a Mode.CTR() with b_iv, and a HMAC() with sign key b_key2
        # b_password = secret.bytes
        b_password = secret

        b_key1, b_key2, b_iv = cls._gen_key_initctr(b_password, b_salt)

        if HAS_CRYPTOGRAPHY:
            b_plaintext = cls._decrypt_cryptography(
                b_ciphertext, b_crypted_hmac, b_key1, b_key2, b_iv
            )
        elif HAS_PYCRYPTO:
            b_plaintext = cls._decrypt_pycrypto(
                b_ciphertext, b_crypted_hmac, b_key1, b_key2, b_iv
            )
        else:
            raise AXC2Error(NEED_CRYPTO_LIBRARY + '(Detected in decrypt)')

        return b_plaintext


u8 = lambda s: bytes(s.encode('utf-8'))
u8s = lambda b: b.decode('utf-8')
AES256Vault.encrypt_text = lambda s, pw: u8s(AES256Vault.encrypt(u8(s), u8(pw)))
AES256Vault.decrypt_to_text = lambda cr, pw: u8s(AES256Vault.decrypt(u8(cr), u8(pw)))


class VaultsByCypher:
    AES256 = AES256Vault


def to_bytes(s, *a, **kw):
    return bytes(s)


encrypt = lambda txt, pw: AES256Vault.encrypt_text(txt, pw)
decrypt = lambda txt, pw: AES256Vault.decrypt_to_text(txt, pw)

if __name__ == '__main__':
    v = AES256Vault
    res = v.encrypt(bytes('foo'.encode('utf-8')), b'bar')
    res = v.decrypt(res, b'bar')
    assert res == b'foo'

    res = v.encrypt_text('foo', 'bar')
    assert v.decrypt_to_text(res, 'bar') == 'foo'
