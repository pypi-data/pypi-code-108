import json
from base64 import b64decode
from enum import Enum, unique
from typing import AsyncIterator, Final, Optional, Tuple, Union, cast

import attr
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.padding import MGF1, OAEP
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey
from cryptography.hazmat.primitives.ciphers import Cipher, CipherContext
from cryptography.hazmat.primitives.ciphers.algorithms import AES
from cryptography.hazmat.primitives.ciphers.modes import CBC
from cryptography.hazmat.primitives.constant_time import bytes_eq
from cryptography.hazmat.primitives.hashes import SHA1, SHA256, SHA512, Hash
from yarl import URL

from aiotgbot import BaseTelegram
from aiotgbot.api_types import EncryptedCredentials

__all__ = ('passport_request', 'PassportKey', 'PassportCipher',
           'PassportScopeType', 'PassportScopeElementOne',
           'PassportScopeElementOneOfSeveral', 'PassportScopeElement',
           'PassportScope', 'FileCredentials', 'DataCredentials',
           'SecureValue', 'SecureData', 'Credentials', 'PersonalDetails',
           'ResidentialAddress', 'IdDocumentData')


def passport_request(bot_id: int, scope: 'PassportScope', public_key: str,
                     nonce: str) -> str:
    url = URL('tg://resolve').with_query(
        domain='telegrampassport',
        bot_id=bot_id,
        scope=json.dumps(scope.to_dict()),
        public_key=public_key,
        nonce=nonce
    )
    return str(url)


class PassportKey:
    _padding: Final[OAEP] = OAEP(mgf=MGF1(algorithm=SHA1()), algorithm=SHA1(),
                                 label=None)

    def __init__(self, private_key: RSAPrivateKey) -> None:
        if not isinstance(private_key, RSAPrivateKey):
            raise RuntimeError('Key is not RSA private key')
        self._private_key: Final[RSAPrivateKey] = private_key
        public_key = self._private_key.public_key()
        public_bytes = public_key.public_bytes(
            serialization.Encoding.PEM,
            serialization.PublicFormat.SubjectPublicKeyInfo
        )
        self._public_key_pem: Final[str] = public_bytes.decode()

    @staticmethod
    def load_der(private_bytes: bytes) -> 'PassportKey':
        private_key = serialization.load_der_private_key(
            private_bytes, password=None)
        return PassportKey(cast(RSAPrivateKey, private_key))

    @staticmethod
    def load_pem(private_text: str) -> 'PassportKey':
        private_key = serialization.load_pem_private_key(
            private_text.encode(), password=None)
        return PassportKey(cast(RSAPrivateKey, private_key))

    def decrypt(self, ciphertext: bytes) -> bytes:
        return self._private_key.decrypt(ciphertext, self._padding)

    @property
    def public_key_pem(self) -> str:
        return self._public_key_pem


class PassportCipher:
    _key_size: Final[int] = 32
    _iv_size: Final[int] = 16

    def __init__(self, data_secret: bytes, data_hash: bytes) -> None:
        digest = Hash(SHA512())
        digest.update(data_secret)
        digest.update(data_hash)
        secret_hash = digest.finalize()
        key = secret_hash[:self._key_size]
        iv = secret_hash[self._key_size:self._key_size + self._iv_size]
        self._data_hash: Final[bytes] = data_hash
        self._cipher: Final[Cipher] = Cipher(AES(key), CBC(iv))

    def decrypt(self, ciphertext: bytes) -> bytes:
        decryptor = self._cipher.decryptor()  # type: ignore
        assert isinstance(decryptor, CipherContext)
        plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        digest = Hash(SHA256())
        digest.update(plaintext)
        computed_hash = digest.finalize()
        if not bytes_eq(computed_hash, self._data_hash):
            raise RuntimeError('Decryption error')
        return plaintext[plaintext[0]:]

    async def decrypt_stream(
        self, stream: AsyncIterator[bytes]
    ) -> AsyncIterator[bytes]:
        decryptor = self._cipher.decryptor()  # type: ignore
        assert isinstance(decryptor, CipherContext)
        digest = Hash(SHA256())
        skip = None
        async for chunk in stream:
            decrypted = decryptor.update(chunk)
            digest.update(decrypted)
            if skip is None:
                skip = decrypted[0]
            if skip >= len(decrypted):
                skip = skip - len(decrypted)
            else:
                yield decrypted[skip:]
                skip = 0
        decrypted = decryptor.finalize()
        digest.update(decrypted)
        computed_hash = digest.finalize()
        if not bytes_eq(computed_hash, self._data_hash):
            raise RuntimeError('Decryption error')
        yield decrypted[skip:]


@unique
class PassportScopeType(Enum):
    PERSONAL_DETAILS = 'personal_details'
    PASSPORT = 'passport'
    DRIVER_LICENSE = 'driver_license'
    IDENTITY_CARD = 'identity_card'
    INTERNAL_PASSPORT = 'internal_passport'
    ADDRESS = 'address'
    UTILITY_BILL = 'utility_bill'
    BANK_STATEMENT = 'bank_statement'
    RENTAL_AGREEMENT = 'rental_agreement'
    PASSPORT_REGISTRATION = 'passport_registration'
    TEMPORARY_REGISTRATION = 'temporary_registration'
    PHONE_NUMBER = 'phone_number'
    EMAIL = 'email'


@attr.s(auto_attribs=True)
class PassportScopeElementOne(BaseTelegram):
    type: PassportScopeType
    selfie: Optional[bool] = None
    translation: Optional[bool] = None
    native_names: Optional[bool] = None


@attr.s(auto_attribs=True)
class PassportScopeElementOneOfSeveral(BaseTelegram):
    one_of: Tuple[PassportScopeElementOne, ...]
    selfie: Optional[bool] = None
    translation: Optional[bool] = None


PassportScopeElement = Union[PassportScopeElementOne,
                             PassportScopeElementOneOfSeveral]


@attr.s(auto_attribs=True)
class PassportScope(BaseTelegram):
    data: Tuple[PassportScopeElement, ...]
    v: int = 1


@attr.s(auto_attribs=True)
class FileCredentials(BaseTelegram):
    file_hash: str
    secret: str


@attr.s(auto_attribs=True)
class DataCredentials(BaseTelegram):
    data_hash: str
    secret: str

    def decrypt(self, ciphertext: str) -> bytes:
        cipher = PassportCipher(b64decode(self.secret),
                                b64decode(self.data_hash))
        return cipher.decrypt(b64decode(ciphertext))


@attr.s(auto_attribs=True)
class SecureValue(BaseTelegram):
    data: Optional[DataCredentials] = None
    front_side: Optional[FileCredentials] = None
    reverse_side: Optional[FileCredentials] = None
    selfie: Optional[FileCredentials] = None
    translation: Optional[Tuple[FileCredentials, ...]] = None
    files: Optional[Tuple[FileCredentials, ...]] = None


@attr.s(auto_attribs=True)
class SecureData(BaseTelegram):
    personal_details: Optional[SecureValue] = None
    passport: Optional[SecureValue] = None
    internal_passport: Optional[SecureValue] = None
    driver_license: Optional[SecureValue] = None
    identity_card: Optional[SecureValue] = None
    address: Optional[SecureValue] = None
    utility_bill: Optional[SecureValue] = None
    bank_statement: Optional[SecureValue] = None
    rental_agreement: Optional[SecureValue] = None
    passport_registration: Optional[SecureValue] = None
    temporary_registration: Optional[SecureValue] = None


@attr.s(auto_attribs=True)
class Credentials(BaseTelegram):
    secure_data: SecureData
    nonce: str

    @staticmethod
    def from_encrypted(encrypted: EncryptedCredentials,
                       passport_key: PassportKey) -> 'Credentials':
        data_secret = passport_key.decrypt(b64decode(encrypted.secret))
        data_hash = b64decode(encrypted.hash)
        ciphertext = b64decode(encrypted.data)
        cipher = PassportCipher(data_secret, data_hash)
        plaintext = cipher.decrypt(ciphertext)
        return Credentials.from_dict(json.loads(plaintext))


@attr.s(auto_attribs=True)
class PersonalDetails(BaseTelegram):
    first_name: str
    last_name: str
    birth_date: str
    gender: str
    country_code: str
    residence_country_code: str
    middle_name: Optional[str] = None
    first_name_native: Optional[str] = None
    last_name_native: Optional[str] = None
    middle_name_native: Optional[str] = None


@attr.s(auto_attribs=True)
class ResidentialAddress(BaseTelegram):
    street_line1: str
    city: str
    country_code: str
    post_code: str
    street_line2: Optional[str] = None
    state: Optional[str] = None


@attr.s(auto_attribs=True)
class IdDocumentData(BaseTelegram):
    document_no: str
    expiry_date: Optional[str] = None
