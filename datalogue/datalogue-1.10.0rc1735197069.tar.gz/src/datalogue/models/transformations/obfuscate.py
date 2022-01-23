import abc
from base64 import b64decode
from typing import Union, List, Optional

from datalogue.errors import DtlError, _enum_parse_error
from datalogue.models.transformations.commons import (
    ByClass,
    ByFieldName,
    Transformation,
)
from datalogue.dtl_utils import (
    _parse_list,
    SerializableStringEnum,
    _parse_string_list,
    EncryptionAlgorithm,
)


class ObfuscationType(abc.ABC):
    """
    Abstract class used to reference the type of Obfuscate to apply to target data

    Contains the three subclasses, each representing an obfuscation type:
    - Encrypt, for two-way encryption
    - Hash, for one-way hash
    - Replace, for one-way string replacement
    """

    type_field = "type"

    def __init__(self, obfuscation_type: str):
        self.type = obfuscation_type
        super().__init__()

    def _base_payload(self) -> dict:
        return dict([(ObfuscationType.type_field, self.type)])

    @abc.abstractmethod
    def _as_payload(self) -> dict:
        """
        Represents the transformation in its dictionary construction
        :return: a dictionary representing this class
        """

    @abc.abstractmethod
    def _from_payload(json: dict) -> Union[DtlError, "ObfuscationType"]:
        """"""


class Obfuscate(Transformation):
    type_str = "Obfuscate"

    def __init__(
        self, targets: List[Union[ByClass, ByFieldName]], obfuscation_type: ObfuscationType,
    ):
        """
        Obfuscate data with hashing, encryption, or string replacement.

        :param target: a list of references to data to target with the obfuscation
        :param obfuscation_type: the type of obfuscation to apply to the data specified by the target. Hash, encryption, or string replacement are available, each with additional parameters.
        """
        Transformation.__init__(self, Obfuscate.type_str)
        self.targets = targets
        self.obfuscation_type = obfuscation_type

    def __repr__(self):
        return "Obfuscate(" f"targets= {self.targets})" f"obfuscation_type= {self.obfuscation_type})"

    def _as_payload(self) -> dict:
        base = self._base_payload()
        targetClassesIds = []
        targetPaths = []

        for elem in self.targets:
            if isinstance(elem, ByClass):
                targetClassesIds.append(str(elem.class_id))
            elif isinstance(elem, ByFieldName):
                targetPaths.append(elem.field_name)

        base["targetClassesIds"] = targetClassesIds
        base["targetPaths"] = targetPaths
        base["obfuscationType"] = self.obfuscation_type._as_payload()
        return base

    @staticmethod
    def _from_payload(json: dict) -> Union[DtlError, "Obfuscate"]:
        obfuscationType = ObfuscationType._from_payload(json.get("obfuscationType"))
        target_paths = _parse_list(_parse_string_list)((json.get("targetPaths")))
        target_classes_ids = _parse_string_list(json.get("targetClassesIds"))
        targets = []
        for elem in target_paths:
            targets.append(ByFieldName(elem))
        for elem in target_classes_ids:
            targets.append(ByClass(elem))
        return Obfuscate(targets, obfuscationType)


class HashAlgorithm(SerializableStringEnum):
    SHA3_512 = "SHA3-512"

    @staticmethod
    def parse_error(s: str) -> DtlError:
        return DtlError(_enum_parse_error("hash algorithm", s))

    @staticmethod
    def hash_algorithm_from_str(string: str) -> Union[DtlError, "HashAlgorithm"]:
        return SerializableStringEnum.from_str(HashAlgorithm)(string)


class Encrypt(ObfuscationType):
    type = "Encrypt"

    def __init__(
        self, key: str, encryption_algorithm: EncryptionAlgorithm = EncryptionAlgorithm.AES_256,
    ):
        """
        Encrypt data referenced by the target parameter of Obfuscate, with later decryption possible via the key supplied.
        The key needs to be a 32-bit base64 encoded string.

        :param encryption_algorithm: the algorithm to use, via the EncryptionAlgorithm class, defaults to AES_256
        :param key: the encryption key for later decryption
        """
        validate_AES256_key(key)
        self.encryption_algorithm = encryption_algorithm
        self.key = key

    def __repr__(self):
        return "Encrypt(" f"encryption_algorithm= {self.encryption_algorithm}), key= {self.key}"

    def _as_payload(self) -> dict:
        res = self._base_payload()
        res["key"] = self.key
        res["encryptionAlgorithm"] = self.encryption_algorithm.value
        return res

    def _from_payload(json: dict) -> Union[DtlError, "Encrypt"]:
        key = json.get("key")
        encryption_algorithm = EncryptionAlgorithm.encryption_algorithm_from_str(json.get("encryptionAlgorithm"))
        return Encrypt(key, encryption_algorithm)


class Decrypt(Transformation):

    type_str = "Decrypt"

    def __init__(
        self,
        key: str,
        targets: List[Union[ByClass, ByFieldName]],
        encryption_algorithm: EncryptionAlgorithm = EncryptionAlgorithm.AES_256,
    ):
        """
        Decrypt data referenced by the target parameters.
        The key needs to be a 32-bit base64 encoded string.

        :param targets: a list of references to data to target with the decryption
        :param encryption_algorithm: the algorithm used to encrypt the data, via the EncryptionAlgorithm class, defaults to AES_256
        :param key: the encryption key to use for decryption
        """
        validate_AES256_key(key)
        Transformation.__init__(self, Decrypt.type_str)
        self.key = key
        self.targets = targets
        self.encryption_algorithm = encryption_algorithm

    def __repr__(self):
        return "Decrypt(" f"targets= {self.targets}," f"encryption_algorithm= {self.encryption_algorithm})"

    def _as_payload(self) -> dict:
        base = self._base_payload()
        targetClassesIds = []
        targetPaths = []

        for elem in self.targets:
            if isinstance(elem, ByClass):
                targetClassesIds.append(str(elem.class_id))
            elif isinstance(elem, ByFieldName):
                targetPaths.append(elem.field_name)

        base["targetClassesIds"] = targetClassesIds
        base["targetPaths"] = targetPaths
        base["encryptionAlgorithm"] = self.encryption_algorithm.value
        base["key"] = self.key
        return base

    def _from_payload(json: dict) -> Union[DtlError, "Decrypt"]:
        key = json.get("key")
        target_paths = _parse_list(_parse_string_list)((json.get("targetPaths")))
        target_classes_ids = _parse_string_list(json.get("targetClassesIds"))
        encryption_algorithm = EncryptionAlgorithm.encryption_algorithm_from_str(json.get("encryptionAlgorithm"))
        targets = []
        for elem in target_paths:
            targets.append(ByFieldName(elem))
        for elem in target_classes_ids:
            targets.append(ByClass(elem))

        return Decrypt(key, targets, encryption_algorithm)


class Replace(ObfuscationType):
    type = "Replace"

    def __init__(
        self, replacement: str, left_offset: Optional[int] = None, right_offset: Optional[int] = None,
    ):
        """
        Replace the data referenced by the target parameter of Obfuscate with a supplied string

        :param replacement: the string to use as replacement
        :param left_offset: can be set to begin the replacement at the specified character count from the beginning of the target string
        :param right_offset: can be set to stop the replacement at the specified character count from the end of the target string
        """
        self.replacement = replacement
        self.left_offset = left_offset
        self.right_offset = right_offset

    def __repr__(self):
        return (
            "Replace("
            f"replacement= {self.replacement}, "
            f"left_offset= {self.left_offset!r}, "
            f"right_offset= {self.right_offset!r})"
        )

    def _as_payload(self) -> dict:
        base = self._base_payload()
        base["replacement"] = self.replacement
        base["leftOffset"] = self.left_offset
        base["rightOffset"] = self.right_offset
        return base

    def _from_payload(json: dict) -> Union[DtlError, "Replace"]:
        replacement = json.get("replacement")
        leftOffset = json.get("leftOffset")
        rightOffset = json.get("rightOffset")
        return Replace(replacement, leftOffset, rightOffset)


class Hash(ObfuscationType):
    type = "Hash"

    def __init__(
        self, hash_algorithm: HashAlgorithm = HashAlgorithm.SHA3_512, salt_hash: Optional[str] = None,
    ):
        """
          Hash the data referenced by the target parameter of Obfuscate

          :param hash_algorithm: the algorithm to use, via the HashAlgorithm class, defaults to SHA3-512
          :param salt_hash: can be used to provide a salt the hash, appending a string to the pre-hashed string and increasing the output’s complexity
        """
        self.hash_algorithm = hash_algorithm
        self.salt_hash = salt_hash

    def __repr__(self):
        return "Hash(" f"hash_algorithm= {self.hash_algorithm}, " f"salt_hash= {self.salt_hash})"

    def _as_payload(self) -> dict:
        base = self._base_payload()
        base["hashAlgorithm"] = self.hash_algorithm.value
        base["salt"] = self.salt_hash
        return base

    def _from_payload(json: dict) -> Union[DtlError, "Hash"]:
        salt = json.get("salt")
        hash_algo = HashAlgorithm.hash_algorithm_from_str(json.get("hash_algorithm"))
        return Hash(hash_algo, salt)


def validate_AES256_key(key: str):
    try:
        if len(b64decode(key.encode("utf-8"))) != 32:
            raise DtlError("Invalid key. Encryption/Decryption key needs to be 256-bit in length")
    except:
        raise DtlError("Invalid key. Encryption/Decryption key needs to be 256-bit in length")
