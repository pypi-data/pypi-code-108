import datetime
import enum

import peewee
from playhouse.sqlcipher_ext import SqlCipherDatabase
from OpenSSL import crypto
from OpenSSL.SSL import FILETYPE_PEM

from .utils import ask_private_key_passphrase

"""
The database filename
"""
DATABASE_FILENAME = 'ca.vault'  # ca.vault

"""
The database filename backup
"""
DATABASE_FILENAME_BACKUP = f'{DATABASE_FILENAME}.bak'

"""
The database object
"""
database = SqlCipherDatabase(None)


class BaseModel(peewee.Model):
    """
    Base model
    """
    class Meta:
        database = database


class BaseCertKeyModel(BaseModel):
    """
    Base certificate model which may have a key.

    The certificate must be stored into the "cert" attribute in the PEM format.
    The optional private key must be stored into the "key" attribute in the PEM format.

    The OpenSSL.crypto.X509 and OpenSSL.crypto.Pkey can be loaded as self.cert_obj and self.key_obj. If the key is
    passphrase protected, the user is asking for this passphrase.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.cert_obj = None
        self.key_obj = None

    def load_cert(self) -> None:
        """
        Load the certificate as OpenSSL.crypto.X509 object into the attribute "cert_obj".
        """
        self.cert_obj = crypto.load_certificate(FILETYPE_PEM, self.cert.encode('utf8'))

    def load_key(self) -> None:
        """
        Load the private key as OpenSSL.crypto.Pkey object into the attribute "key_obj".

        If the key is passphrase protected, the user is asking for this passphrase (prompt to stdout, read from stdin).

        If no key is available (self.key is None), a RuntimeError is raised.

        :except: RunTime
        """
        if not self.key:
            raise RuntimeError('No key available')

        self.key_obj = crypto.load_privatekey(FILETYPE_PEM, self.key.encode('utf8'),
                                              passphrase=ask_private_key_passphrase)

    def clear_key(self) -> None:
        """
        Clear the attribute "key_obj".
        """
        self.key_obj = None


class CA(BaseCertKeyModel):
    """
    A Certificate Authority model.

    The certificate and the key are stored in the PEM format.
    """
    id = peewee.IntegerField(primary_key=True)
    name = peewee.CharField(unique=True)
    cert = peewee.TextField()
    key = peewee.TextField()


class CertificateRevokedReason(enum.Enum):
    """
    The certificate revoked reason
    """
    UNSPECIFIED = 'unspecified'
    KEY_COMPRISE = 'keyCompromise'
    CESSATION_OF_OPERATION = 'cessationOfOperation'


class Certificate(BaseCertKeyModel):
    """
    A certificate model.

    The created_timestamp and not_after are precise to the second.
    The serial is provided in the official X509 output, so in hex format using ":" separator in the big endian
    representation of the 64 bits integer.
    The certificate and the key (optional) are stored in the PEM format.
    """
    id = peewee.IntegerField(primary_key=True)
    cn = peewee.CharField()
    san = peewee.CharField(null=True)
    created_timestamp = peewee.DateTimeField()
    not_after = peewee.DateTimeField()
    serial = peewee.CharField()
    cert = peewee.TextField()
    key = peewee.TextField(null=True)
    is_revoked = peewee.BooleanField()
    revoked_timestamp = peewee.DateTimeField(null=True)
    revoked_reason = peewee.BlobField(null=True)
    revoked_comment = peewee.TextField(null=True)
    is_renewed = peewee.BooleanField()
    renewed_cert_id = peewee.IntegerField(null=True)

    def __str__(self):
        now = datetime.datetime.now()

        s = f'#{self.id}. CN:{self.cn}'\

        if self.san:
            s += f' / {self.san}'

        s += ' ('

        if self.is_renewed:
            s += 'renewed'
        elif self.is_revoked:
            s += 'revoked'

            if self.revoked_comment:
                s += f' [reason: {self.revoked_comment}]'
        elif self.not_after <= now:
            s += 'expired'
        else:
            s += f'expire on {self.not_after.strftime("%d/%m/%Y %H:%M:%S")}'

        s += f', serial : {self.serial}'

        if not self.key:
            s += ', no private key'

        s += ')'

        return s


class CRL(BaseModel):
    """
    A Certificate Revoked List model

    The crl_timestamp is precise to the second.
    """
    id = peewee.IntegerField(primary_key=True)
    crl_version = peewee.IntegerField()
    crl_timestamp = peewee.DateTimeField()
    crl = peewee.TextField()


class ConfigType(enum.IntEnum):
    """
    The configuration value type
    """
    INT = 1
    STRING = 2
    BINARY = 3


class Config(BaseModel):
    """
    A Configuration model
    """
    name = peewee.CharField(primary_key=True)
    type = peewee.IntegerField()
    value = peewee.CharField()
