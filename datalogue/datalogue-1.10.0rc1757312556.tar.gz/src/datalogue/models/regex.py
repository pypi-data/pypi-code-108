from enum import Enum
from typing import Optional, List, Union

from datalogue.errors import DtlError, _enum_parse_error
from datalogue.dtl_utils import (
    SerializableStringEnum,
    exists,
    _parse_datetime,
    _parse_uuid,
    _parse_list,
    map_option,
)
from uuid import UUID
from datetime import datetime


class SearchOrder(Enum):
    created_at_asc = ("CreatedAt", "Asc")
    created_at_desc = ("CreatedAt", "Desc")
    updated_at_desc = ("UpdatedAt", "Desc")
    updated_at_asc = ("UpdatedAt", "Asc")


class RegexStatus(SerializableStringEnum):
    NoMatch = "NoMatch"
    PerfectMatch = "PerfectMatch"

    @staticmethod
    def parse_error(s: str) -> str:
        return DtlError(_enum_parse_error("regex status", s))

    @staticmethod
    def from_str(string: str) -> Union[DtlError, "RegexStatus"]:
        return SerializableStringEnum.from_str(RegexStatus)(string)


class RegexTestSample:
    """
    Representation for test samples for Regex. It contains a text value and 
    optionally a status to denote whether it's a Match or NoMatch
    """

    def __init__(self, text: str, status: Optional[RegexStatus] = None):
        self.text = text
        self.status = status

    def __repr__(self):
        return "\n  RegexTestSample(" f"text= {self.text!r}, " f"status= {self.status})"

    def __eq__(self, other):
        return (self.text == other.text) and (self.status == other.status)

    @staticmethod
    def _as_payload(sample: "RegexTestSample") -> Union[DtlError, dict]:
        payload = {"text": sample.text}
        if sample.status is not None:
            payload["status"] = sample.status.value
        return payload

    @staticmethod
    def _from_payload(payload: dict) -> Union[DtlError, "Regex"]:
        text = payload.get("text")
        if text is None:
            return DtlError("'text' is missing! Invalid json for RegexTestSample")
        status = map_option(payload.get("status"), RegexStatus.from_str)
        return RegexTestSample(text, status)


class Regex:
    """
    Representation for regexes.
    """

    def __init__(
        self,
        name: str,
        pattern: str,
        description: str = "",
        test_data: Optional[Union[List[str], List[RegexTestSample]]] = [],
        id: Optional[UUID] = None,
        owner: Optional[UUID] = None,
        editors: Optional[List[UUID]] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        updated_by: Optional[UUID] = None,
    ):
        self.id = id
        self.name = name
        self.pattern = pattern
        self.description = description
        if test_data is not None and all(isinstance(test_datum_text, str) for test_datum_text in test_data):
            self.test_data = list(map(lambda test_datum: RegexTestSample(test_datum), test_data))
        elif test_data is not None and all(
            isinstance(test_datum_text, RegexTestSample) for test_datum_text in test_data
        ):
            self.test_data = test_data
        elif test_data is None:
            self.test_data = test_data
        else:
            raise DtlError("Please provide either list of strings or list of RegexTestSample for test_data parameters.")
        self.owner = owner
        self.editors = editors
        self.created_at = created_at
        self.updated_at = updated_at
        self.updated_by = updated_by

    def __eq__(self, other):
        return (
            (self.name == other.name)
            and (self.pattern == other.pattern)
            and (self.description == other.description)
            and (self.test_data == other.test_data)
            and (self.owner == other.owner)
            and (self.editors == other.editors)
            and (self.created_at == other.created_at)
            and (self.updated_at == other.updated_at)
            and (self.updated_by == other.updated_by)
        )

    def __repr__(self):
        return (
            "Regex("
            f"id= {self.id!r}, "
            f"name= {self.name!r}, "
            f"pattern= {self.pattern!r},  "
            f"description= {self.description!r}, "
            f"test_data= {self.test_data})"
        )

    @staticmethod
    def _as_payload(regex: "Regex") -> Union[DtlError, dict]:
        payload = {
            "name": regex.name,
            "pattern": regex.pattern,
            "description": regex.description,
            "testData": list(map(lambda t: RegexTestSample._as_payload(t), regex.test_data)),
        }

        if regex.id is not None:
            payload["id"] = regex.id

        if regex.owner is not None:
            payload["owner"] = regex.owner

        if regex.editors is not None:
            payload["editors"] = regex.editors

        if regex.created_at is not None:
            payload["createdAt"] = regex.created_at

        if regex.updated_at is not None:
            payload["updatedAt"] = regex.updated_at

        if regex.updated_by is not None:
            payload["lastUpdateBy"] = regex.updated_by

        return payload

    @staticmethod
    def _from_payload(payload: dict) -> Union[DtlError, "Regex"]:
        name = payload.get("name")
        if name is None or not isinstance(name, str):
            return DtlError("'name' is missing or not a string")

        pattern = payload.get("pattern")
        if pattern is None or not isinstance(pattern, str):
            return DtlError("'pattern' is missing or not a string")

        description = payload.get("description")
        if description is None or not isinstance(description, str):
            return DtlError("'description' is missing or not a string")

        test_data_jsons = payload.get("testData")
        if test_data_jsons is None or not isinstance(test_data_jsons, List):
            return DtlError("'testData' is missing or not a List")

        test_data = _parse_list(RegexTestSample._from_payload)(test_data_jsons)
        if isinstance(test_data, DtlError):
            return test_data

        id = map_option(payload.get("id"), _parse_uuid)
        owner = map_option(payload.get("owner"), _parse_uuid)

        editors = payload.get("editors")
        if editors is not None:
            editors = _parse_list(_parse_uuid)(editors)
            if isinstance(editors, DtlError):
                return DtlError(f"'editors has at least one invalid value: {payload.get('editors')}", editors,)

        created_at = map_option(payload.get("createdAt"), _parse_datetime)
        if isinstance(created_at, DtlError):
            return created_at

        updated_at = map_option(payload.get("updatedAt"), _parse_datetime)
        if isinstance(updated_at, DtlError):
            return updated_at

        updated_by = map_option(payload.get("lastUpdateBy"), _parse_uuid)
        if isinstance(updated_by, DtlError):
            return updated_by

        return Regex(name, pattern, description, test_data, id, owner, editors, created_at, updated_at, updated_by,)
