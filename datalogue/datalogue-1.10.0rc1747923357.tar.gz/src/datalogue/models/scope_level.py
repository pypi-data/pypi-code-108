from typing import Union

from datalogue.errors import DtlError, _enum_parse_error
from datalogue.dtl_utils import SerializableStringEnum


class Scope(SerializableStringEnum):
    User = "User"
    Group = "Group"
    Organization = "Organization"

    @staticmethod
    def parse_error(s: str) -> str:
        return DtlError(_enum_parse_error("share target", s))

    @staticmethod
    def from_string(string: str) -> Union[DtlError, "Scope"]:
        return SerializableStringEnum.from_str(Scope)(string)
