from datalogue.models.transformations.commons import Transformation, DataType
from datalogue.dtl_utils import _parse_string_list, SerializableStringEnum
from datalogue.errors import (
    _enum_parse_error,
    DtlError,
    _property_not_found,
    _invalid_property_type,
)
from typing import List, Union


class Period:
    def __init__(self, identifier: str, value: int, unit: str):
        self.identifier = identifier
        self.value = value
        self.unit = unit

    def __eq__(self, other: "Period"):
        if isinstance(self, other.__class__):
            return self._as_payload() == other._as_payload()
        return False

    def __repr__(self):
        return f"Period(identifier= {self.identifier}, value= {self.value}, unit= {self.unit})"

    def _as_payload(self) -> dict:
        return {"identifier": self.identifier, "value": self.value, "unit": self.unit}

    @staticmethod
    def _from_payload(json: dict) -> Union[DtlError, "Period"]:
        identifier = json.get("identifier")
        if identifier is None:
            return _property_not_found("identifier", json)

        value = json.get("value")
        if value is None:
            return _property_not_found("value", json)

        unit = json.get("unit")
        if unit is None:
            return _property_not_found("unit", json)

        return Period(identifier, value, unit)


class Format:
    def __init__(self, start: str, end: str, separator: str):
        self.start = start
        self.end = end
        self.separator = separator

    def __eq__(self, other: "Format"):
        if isinstance(self, other.__class__):
            return self._as_payload() == other._as_payload()
        return False

    def __repr__(self):
        return f"Format(start= {self.start}, end= {self.end}, separator= {self.separator})"

    def _as_payload(self) -> dict:
        return {"start": self.start, "separator": self.separator, "end": self.end}

    @staticmethod
    def _from_payload(json: dict) -> Union[DtlError, "Format"]:
        start = json.get("start")
        if start is None:
            return _property_not_found("start", json)

        separator = json.get("separator")
        if separator is None:
            return _property_not_found("separator", json)

        end = json.get("end")
        if end is None:
            return _property_not_found("end", json)

        return Format(start, end, separator)


class Output:
    def __init__(self, start_label: str, end_label: str, format: str):
        self.start_label = start_label
        self.end_label = end_label
        self.format = format

    def __eq__(self, other: "Output"):
        if isinstance(self, other.__class__):
            return self._as_payload() == other._as_payload()
        return False

    def __repr__(self):
        return f"Output(start= {self.start_label}, end= {self.end_label}, separator= {self.format})"

    def _as_payload(self) -> dict:
        return {
            "startLabel": self.start_label,
            "endLabel": self.end_label,
            "format": self.format,
        }

    @staticmethod
    def _from_payload(json: dict) -> Union[DtlError, "Output"]:
        start_label = json.get("startLabel")
        if start_label is None:
            return _property_not_found("startLabel", json)

        end_label = json.get("endLabel")
        if end_label is None:
            return _property_not_found("endLabel", json)

        format = json.get("format")
        if format is None:
            return _property_not_found("format", json)

        return Output(start_label, end_label, format)
