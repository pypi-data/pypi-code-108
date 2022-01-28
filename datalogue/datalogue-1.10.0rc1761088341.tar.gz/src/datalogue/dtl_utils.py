from hashlib import pbkdf2_hmac
from base64 import b64encode
from uuid import UUID
from typing import TypeVar, List, Callable, Union, Dict, Type, Optional
from enum import Enum
from abc import abstractmethod, ABC
from io import BytesIO, SEEK_SET, SEEK_END
import random
from datetime import datetime
from dateutil.parser import parse

from pbkdf2 import PBKDF2

from datalogue.errors import DtlError, _enum_parse_error


hardcoded_salt = b"\xc7H\x94\x80l\x9f\x8f\t"
T = TypeVar("T")
R = TypeVar("R")
Json = Union[Dict, str, int, List]


def generate_salt(password: str) -> Union[DtlError, str]:
    """
    Generate a hexadecimal string usable for salting by an hash algorithm based on a simple password

    :param password: a simple password that can be used to generate a hexadecimal string appropriate for salting a hash
    :return: a hexadecimal string, if successful, or DtlError if failed
    """
    if not isinstance(password, str):
        return DtlError("Passwords need to be a string type!")
    salt = pbkdf2_hmac("sha512", password.encode("utf-8"), hardcoded_salt, 100000)

    return salt.hex()


def exists(func, iterable) -> bool:
    for i in iterable:
        if func(i) is True:
            return True
    return False


def map_option(optional_value: Optional[T], function: Callable[[T], R]) -> Optional[R]:
    if optional_value is None:
        return None
    else:
        return function(optional_value)


def _parse_datetime(value: str) -> Union[DtlError, datetime]:
    try:
        datetime_value = parse(value)
        return datetime_value
    except ValueError:
        return DtlError(f"Given value: {value} is not a proper datetime!")


def _parse_uuid(value: Union[str, UUID], error_message: Optional[str] = None) -> Union[DtlError, UUID]:
    if isinstance(value, UUID):
        return value
    try:
        uuid_value = UUID(value)
        return uuid_value
    except ValueError:
        if error_message is None:
            return DtlError(f"Given value: {value} is not a proper UUID!")
        else:
            return DtlError(error_message)


def _parse_list(
    parse_function: Callable[[Json], Union[DtlError, T]]
) -> Callable[[List[Json]], Union[DtlError, List[T]]]:
    """
    Returns another function that can be used to parse a list of json with the specified parse function

    :param parse_function: function to be used for parsing
    :return:
    """

    def parse_concrete(objects: List[Json]) -> Union[DtlError, List[T]]:
        """
        Applies the parse function specified in the parent function to each element of the list of json

        :param objects: list to apply the parse function to
        :return:
        """
        parsed_list = []
        for obj in objects:
            parsed_obj = parse_function(obj)

            if isinstance(parsed_obj, DtlError):
                return parsed_obj
            else:
                parsed_list.append(parsed_obj)

        return parsed_list

    return parse_concrete


def _parse_string_list(objects: List[Json]) -> Union[DtlError, List[str]]:
    parsed_list = []

    for obj in objects:
        if isinstance(obj, str):
            parsed_list.append(obj)
        else:
            return DtlError("The following object is not a string: %s" % obj)

    return parsed_list


def not_implemented() -> NotImplemented:
    return NotImplemented


def random_alpha_numeric_string() -> str:
    alphabet = "".join(random.choice("abcdefghijklmnopqrstuvqxyz") for i in range(5))
    numeric = "".join(random.choice("0123456789") for i in range(3))
    return alphabet + numeric


def random_alpha_numeric_string_with_special_chars() -> str:
    alpha_numeric = random_alpha_numeric_string()
    special_chars = "".join(random.choice("""!#$%&'*+-/=?^_`{|}~""") for i in range(3))
    return alpha_numeric + special_chars


def is_valid_uuid(val):
    uuid_or_not = _parse_uuid(val)
    if isinstance(uuid_or_not, UUID):
        return True
    else:
        return False


class SerializableStringEnum(Enum):
    @staticmethod
    def from_str(enum: Type["SerializableStringEnum"],) -> Callable[[str], Union[DtlError, "SerializableStringEnum"]]:
        """
        Builds a function to parse the string enum `enum`
        :param enum: enum to create a parser for
        :return:
        """

        def inner_sanctum(s: str) -> Union[DtlError, "SerializableStringEnum"]:
            """
            Parses a string and returns the instance of the Enum it corresponds to or a string with an error message

            :param s: string to be parsed
            :return:
            """
            for blob_type in enum:
                if blob_type.value == s:
                    return blob_type

            return enum.parse_error(s)

        return inner_sanctum

    def __repr__(self):
        return f"{self._value_}"

    @staticmethod
    @abstractmethod
    def parse_error(s: str) -> DtlError:
        """
        Returns the error to be used if the parsing fails
        :return: string error
        """
        return s

    @classmethod
    def values(cls):
        """
        Returns the list of all enum values defined in the class
        """
        return list(map(lambda c: c.value, cls))


class ResponseStream(object):
    def __init__(self, request_iterator):
        """
        Class used internally to be able to transform a `requests` iterator into a File like object.

        :param request_iterator: Iterator to pull the data from
        """

        # In memory bytes buffer
        self._bytes = BytesIO()
        # Iterator to use to retrieve data
        self._iterator = request_iterator

        self.closed = self._bytes.closed

    def close(self):
        return self._bytes.close()

    def _load_all(self) -> int:
        """
        Loads all the data into the buffer

        :return: new absolute position in the buffer
        """
        self._bytes.seek(0, SEEK_END)
        for chunk in self._iterator:
            self._bytes.write(chunk)

    def _load_until(self, goal_position: int) -> None:
        """
        Loads the data into the inner buffer until the goal position

        :param goal_position: Byte index to go to
        :return:
        """

        # End of the byte buffer
        current_position = self._bytes.seek(0, SEEK_END)

        # Fill the buffer with more data until we reach the new byte index goal
        while current_position < goal_position:
            try:
                current_position += self._bytes.write(next(self._iterator))
            except StopIteration:
                break

    def tell(self) -> int:
        """
        Current file position, an integer.

        :return:
        """
        return self._bytes.tell()

    def read(self, size=None) -> bytes:
        """
        Read at most size bytes, returned as a bytes object.

        :param size: in bytes to retrieve, if negative reads all
        :return: byte object
        """
        left_off_at = self._bytes.tell()

        # Fill the buffer with new data from the iterator
        if size is None:
            self._load_all()
        else:
            goal_position = left_off_at + size
            self._load_until(goal_position)

        # make sure we are reading from the right position
        self._bytes.seek(left_off_at)

        # return the size bytes from the buffer
        return self._bytes.read(size)

    def seek(self, position, whence=SEEK_SET) -> int:
        """

        :param position:
        :param whence:
        :return:
        """
        if whence == SEEK_END:
            self._load_all()
            return self._bytes.seek(position, whence)
        else:
            return self._bytes.seek(position, whence)


class EncryptionAlgorithm(SerializableStringEnum):
    AES_256 = "AES256"

    @staticmethod
    def parse_error(s: str) -> DtlError:
        return DtlError(_enum_parse_error("encryption algorithm", s))

    @staticmethod
    def encryption_algorithm_from_str(string: str,) -> Union[DtlError, "EncryptionAlgorithm"]:
        return SerializableStringEnum.from_str(EncryptionAlgorithm)(string)


def generate_key(
    password: str, encryption_algorithm: EncryptionAlgorithm = EncryptionAlgorithm.AES_256,
) -> Union[DtlError, str]:
    """
        Generate a key usable by an encryption algorithm based on a simple password

        :param password: a simple password that can be used to generate a key appropriate for encryption
        :param encryption_algorithm: the algorithm that will be used along with the encryption key
        :return: an encryption key as a string, if successful, or DtlError if failed
    """
    if not isinstance(password, str):
        return DtlError("Passwords need to be a string type!")
    if encryption_algorithm == EncryptionAlgorithm.AES_256:
        # Because we just want a mapping of password -> key, we use a hardcoded salt. Use of PBKDF2 is retained because of its useful password -> key generation.
        key = PBKDF2(password, hardcoded_salt).read(32)
        # We'll have to decode the bytestring in UTF-8,
        return b64encode(key).decode("utf-8")
    else:
        return DtlError("Encryption algorithm unknown")
