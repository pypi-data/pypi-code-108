import abc
from typing import Union

from datalogue.errors import DtlError
from datalogue.models.datastore import EncryptionType


class Encryption(abc.ABC):
    type_field = "type"

    def __init__(self, definition_type: EncryptionType):
        self.type = definition_type

    def _base_payload(self) -> dict:
        return dict([(Encryption.type_field, self.type.value)])

    def __eq__(self, other: "Encryption"):
        if isinstance(self, other.__class__):
            return self._as_payload() == other._as_payload()
        return False

    @abc.abstractmethod
    def _as_payload(self) -> dict:
        """
        Dictionary representation of the object
        :return:
        """


class AES256(Encryption):
    def __init__(self):
        Encryption.__init__(self, EncryptionType.AES256)

    def _as_payload(self):
        return self._base_payload()


class KeyId(Encryption):
    def __init__(self, key_id: str):
        Encryption.__init__(self, EncryptionType.KeyId)
        self.keyId = key_id

    def _as_payload(self) -> dict:
        base = self._base_payload()
        base["keyId"] = self.keyId
        return base


class CustomerKey(Encryption):
    def __init__(self, key: str):
        Encryption.__init__(self, EncryptionType.CustomerKey)
        self.key = key

    def _as_payload(self) -> dict:
        base = self._base_payload()
        base["key"] = self.key
        return base
