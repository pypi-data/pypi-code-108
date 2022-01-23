import abc
from typing import List, Optional, Union
from datalogue.errors import DtlError, _property_not_found, _invalid_property_type, _enum_parse_error
from datetime import datetime
from datalogue.models.transformations.commons import Transformation, DataType
from datalogue.dtl_utils import _parse_list, SerializableStringEnum


class NodeDescription:
    """
    Description of a node to be added to the tree.
    """

    def __init__(
        self, path: List[str], value: Union[str, bool, int, float, datetime], value_type: DataType,
    ):
        """
        :param path: path of the node to be created
        :param value: value to be set for the node
        :param value_type: type of the value to be used
        """
        self.path = path
        self.value = value
        self.value_type = value_type

    def __eq__(self, other: "NodeDescription"):
        if isinstance(self, other.__class__):
            return self._as_payload() == other._as_payload()
        return False

    def __repr__(self):
        return f"NodeDescription(path= {'.'.join(self.path)}, value= {self.value!r}, type= {self.value_type!r})"

    def _as_payload(self) -> Union[DtlError, dict]:
        value = self.value
        if isinstance(value, datetime):
            value = value.isoformat()
        else:
            value = str(value)

        return {"path": self.path, "value": value, "valueType": self.value_type.value}

    @staticmethod
    def _from_payload(json: dict) -> Union[DtlError, "NodeDescription"]:
        path = json.get("path")
        if path is None:
            return _property_not_found("path", json)
        elif not isinstance(path, list):
            return _invalid_property_type("path", "List[str]", json)

        value = json.get("value")
        if value is None:
            return _property_not_found("value", json)
        elif not isinstance(value, str):
            return _invalid_property_type("value", "str", json)

        value_type = json.get("valueType")
        if value_type is None:
            return _property_not_found("valueType", json)
        else:
            value_type = DataType.from_str(value_type)
            if isinstance(value_type, DtlError):
                return value_type

        return NodeDescription(path, value, value_type)


class Add(Transformation):
    """
    Adds a node to the graph

    Some edge cases:
        - If the specified path's parent do not exists, the node will not be created
        - If the cast cannot happen for the given value, the node will node be created
    """

    type_str = "Add"

    def __init__(self, nodes: List[NodeDescription]):
        """
        :param nodes: List of nodes to be added to the tree
        """
        Transformation.__init__(self, Add.type_str)
        self.nodes = nodes

    def __eq__(self, other: "Add"):
        if isinstance(self, other.__class__):
            return self._as_payload() == other._as_payload()
        return False

    def __repr__(self):
        return f"Add(nodes= {self.nodes})"

    def _as_payload(self) -> dict:
        base = self._base_payload()
        base["nodes"] = list(map(lambda x: x._as_payload(), self.nodes))
        return base

    @staticmethod
    def _from_payload(json: dict) -> Union[DtlError, "Add"]:
        nodes = json.get("nodes")
        if nodes is None:
            return _property_not_found("nodes", json)

        nodes = _parse_list(NodeDescription._from_payload)(nodes)
        if isinstance(nodes, DtlError):
            return nodes

        return Add(nodes)


class TimeFormat(abc.ABC):
    type_field = "type"

    def __init__(self, time_format_type: str):
        self.type = time_format_type
        super().__init__()

    def __eq__(self, other: "TimeFormat"):
        if isinstance(self, other.__class__):
            return self._as_payload() == other._as_payload()
        return False

    def _base_payload(self) -> dict:
        base = [(TimeFormat.type_field, self.type)]
        return dict(base)

    @abc.abstractmethod
    def _as_payload(self) -> dict:
        """
        Represents the custom type in its dictionary construction

        :return:
        """


class EpochSeconds(TimeFormat):
    type_str = "EpochSeconds"

    def __init__(self):
        TimeFormat.__init__(self, EpochSeconds.type_str)

    def __repr__(self):
        return EpochSeconds.type_str

    def _as_payload(self) -> dict:
        base = self._base_payload()
        return base

    @staticmethod
    def _from_payload(json: dict) -> Union[DtlError, "EpochSeconds"]:
        return EpochSeconds()


class EpochMillis(TimeFormat):
    type_str = "EpochMillis"

    def __init__(self):
        TimeFormat.__init__(self, EpochMillis.type_str)

    def __repr__(self):
        return EpochMillis.type_str

    def _as_payload(self) -> dict:
        base = self._base_payload()
        return base

    @staticmethod
    def _from_payload(json: dict) -> Union[DtlError, "EpochMillis"]:
        return EpochMillis()


def _time_format_from_payload(json: dict) -> Union[DtlError, "TimeFormat"]:
    type_str = json.get(TimeFormat.type_field)
    if type_str is None:
        return _property_not_found("type", json)
    if type_str == EpochSeconds.type_str:
        time_format = EpochSeconds._from_payload(json)
    elif type_str == EpochMillis.type_str:
        time_format = EpochMillis._from_payload(json)
    else:
        return DtlError("'%s' time format is not handled by the SDK" % type_str)
    return time_format


class CustomType(abc.ABC):
    type_field = "type"

    def __init__(self, custom_type: str):
        self.type = custom_type
        super().__init__()

    def __eq__(self, other: "CustomType"):
        if isinstance(self, other.__class__):
            return self._as_payload() == other._as_payload()
        return False

    def _base_payload(self) -> dict:
        base = [(CustomType.type_field, self.type)]
        return dict(base)

    @abc.abstractmethod
    def _as_payload(self) -> dict:
        """
        Represents the custom type in its dictionary construction

        :return:
        """


class RootName(CustomType):
    type_str = "RootName"

    def __init__(self):
        CustomType.__init__(self, RootName.type_str)

    def __repr__(self):
        return RootName.type_str

    def _as_payload(self) -> dict:
        base = self._base_payload()
        return base

    @staticmethod
    def _from_payload(json: dict) -> Union[DtlError, "RootName"]:
        return RootName()


class RecordProcessingTimestamp(CustomType):
    type_str = "RecordProcessingTimestamp"

    def __init__(self, time_format: Optional["TimeFormat"] = None):
        CustomType.__init__(self, RecordProcessingTimestamp.type_str)
        self.time_format = time_format

    def __repr__(self):
        return f"RecordProcessingTimestamp(timeFormat= {self.time_format!r})"

    def _as_payload(self) -> dict:
        base = self._base_payload()
        if self.time_format is not None:
            base["timeFormat"] = self.time_format._as_payload()
        return base

    @staticmethod
    def _from_payload(json: dict) -> Union[DtlError, "RecordProcessingTimestamp"]:
        time_format_dict = json.get("timeFormat")
        if time_format_dict is not None:
            time_format = _time_format_from_payload(time_format_dict)
        else:
            time_format = None
        return RecordProcessingTimestamp(time_format)


class StringConstant(CustomType):
    type_str = "StringConstant"

    def __init__(self, custom_value: str):
        CustomType.__init__(self, StringConstant.type_str)
        self.custom_value = custom_value

    def __repr__(self):
        return f"StringConstant(customValue= {self.custom_value})"

    def _as_payload(self) -> dict:
        base = self._base_payload()
        base["customValue"] = self.custom_value
        return base

    @staticmethod
    def _from_payload(json: dict) -> Union[DtlError, "StringConstant"]:
        custom_value = json.get("customValue")
        if custom_value is None:
            return _property_not_found("customValue", json)
        return StringConstant(custom_value)


class JobRunAt(CustomType):
    type_str = "JobRunAt"

    def __init__(self):
        CustomType.__init__(self, JobRunAt.type_str)

    def _as_payload(self) -> dict:
        base = self._base_payload()
        return base

    def __repr__(self):
        return JobRunAt.type_str

    @staticmethod
    def _from_payload(json: dict) -> Union[DtlError, "JobRunAt"]:
        return JobRunAt()


def _custom_type_from_payload(json: dict) -> Union[DtlError, CustomType]:
    type_str = json.get(CustomType.type_field)
    if type_str is None:
        return _property_not_found("type", json)
    if type_str == RootName.type_str:
        custom_type = RootName._from_payload(json)
    elif type_str == RecordProcessingTimestamp.type_str:
        custom_type = RecordProcessingTimestamp._from_payload(json)
    elif type_str == StringConstant.type_str:
        custom_type = StringConstant._from_payload(json)
    elif type_str == JobRunAt.type_str:
        custom_type = JobRunAt._from_payload(json)
    else:
        return DtlError("'%s' custom type is not handled by the SDK" % type_str)
    return custom_type


class NodeWithCustomValue:
    """
    Description of a node encapsulating a custom value to be added to the tree.
    """

    def __init__(self, path: List[str], custom_type: CustomType):
        """
        :param path: path of the node to be created
        :param custom_type: value to be set for the node
        """
        self.path = path
        self.custom_type = custom_type

    def __eq__(self, other: "NodeWithCustomValue"):
        if isinstance(self, other.__class__):
            return self._as_payload() == other._as_payload()
        return False

    def __repr__(self):
        return f"NodeWithCustomValue(path= {'.'.join(self.path)}, custom_type= {self.custom_type!r})"

    def _as_payload(self) -> Union[DtlError, dict]:
        return {"path": self.path, "customType": self.custom_type._as_payload()}

    @staticmethod
    def _from_payload(json: dict) -> Union[DtlError, "NodeWithCustomValue"]:
        path = json.get("path")
        if path is None:
            return _property_not_found("path", json)
        elif not isinstance(path, list):
            return _invalid_property_type("path", "List[str]", json)
        custom_type_dict = json.get("customType")
        if custom_type_dict is None:
            return _property_not_found("customType", json)
        custom_type = _custom_type_from_payload(custom_type_dict)
        if isinstance(custom_type, DtlError):
            return custom_type
        return NodeWithCustomValue(path, custom_type)


class AddWithCustomValue(Transformation):
    """
    Adds a field to the record with a custom value.
    """

    type_str = "AddWithCustomValue"

    def __init__(self, nodes: List[NodeWithCustomValue]):
        """
        :param nodes: List of nodes to be added to the tree
        """
        Transformation.__init__(self, AddWithCustomValue.type_str)
        self.nodes = nodes

    def __eq__(self, other: "AddWithCustomValue"):
        if isinstance(self, other.__class__):
            return self._as_payload() == other._as_payload()
        return False

    def __repr__(self):
        return f"AddWithCustomValue(nodes= {self.nodes})"

    def _as_payload(self) -> dict:
        base = self._base_payload()
        base["nodes"] = list(map(lambda x: x._as_payload(), self.nodes))
        return base

    @staticmethod
    def _from_payload(json: dict) -> Union[DtlError, "AddWithCustomValue"]:
        nodes = json.get("nodes")
        if nodes is None:
            return _property_not_found("nodes", json)

        nodes = _parse_list(NodeWithCustomValue._from_payload)(nodes)
        if isinstance(nodes, DtlError):
            return nodes

        return AddWithCustomValue(nodes)
