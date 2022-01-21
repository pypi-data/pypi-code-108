from typing import List, Union, Optional
from uuid import UUID

from datalogue.dtl_utils import (
    _parse_string_list,
    _parse_list,
    SerializableStringEnum,
)
from datalogue.errors import DtlError, _property_not_found, _enum_parse_error
from datalogue.models.datastore import (
    Datastore,
    _datastore_def_from_payload,
    DatastoreDef,
)
from datalogue.models.transformations.add import (
    Add,
    AddWithCustomValue,
    CustomType,
    EpochMillis,
    EpochSeconds,
    JobRunAt,
    NodeDescription,
    NodeWithCustomValue,
    RecordProcessingTimestamp,
    RootName,
    StringConstant,
)
from datalogue.models.transformations.append_index_to_label import AppendIndexToLabel
from datalogue.models.transformations.casts import ToDate, ToInt, ToDouble, JsonStringify, FormatDate, ToMacAddress, ToUUID
from datalogue.models.transformations.classify import Classify
from datalogue.models.transformations.commons import Transformation, _array_from_dict, RegexTransformation, DataType
from datalogue.models.transformations.concatenate import ConcatenateAtPaths, MergeFields
from datalogue.models.transformations.flat_map import FlatMap
from datalogue.models.transformations.map_function import MapFunction
from datalogue.models.transformations.math import Math
from datalogue.models.transformations.move_by_regex import MoveByRegex
from datalogue.models.transformations.obfuscate import Obfuscate, Decrypt
from datalogue.models.transformations.split_label_and_value import SplitLabelAndValue
from datalogue.models.transformations.structure import Structure


#############################################################################################
#                                    ADG Transformations
#############################################################################################


class Split(Transformation):
    """
    Splits the tree into list of trees. Each new tree is formed by the root node found at the given path
    and all its children recursively.
    """

    type_str = "Split"

    def __init__(self, path: List[str]):
        Transformation.__init__(self, Split.type_str)
        self.path = path

    def __eq__(self, other: "Split"):
        if isinstance(self, other.__class__):
            return self._as_payload() == other._as_payload()
        return False

    def __repr__(self):
        return f"Split(path= {'.'.join(self.path)})"

    def _as_payload(self) -> dict:
        base = self._base_payload()
        base["path"] = self.path
        return base


def _split_transformation_from_payload(json: dict) -> Union[DtlError, Split]:
    array = _array_from_dict(json, Split.type_str, "path")
    if isinstance(array, DtlError):
        return array

    return Split(array)


class Flatten(Transformation):
    """
    Places all leaf nodes in the tree as children of the root node. All intermediate nodes are removed. Labels
    of leaf nodes are updated to reflect the materialized path they used to have with the delimiter parameter.
    """

    type_str = "Flatten"

    def __init__(self, delimiter: str):
        Transformation.__init__(self, Flatten.type_str)
        self.delimiter = delimiter

    def __eq__(self, other: "Flatten"):
        if isinstance(self, other.__class__):
            return self._as_payload() == other._as_payload()
        return False

    def __repr__(self):
        return f"Flatten(delimiter= {self.delimiter})"

    def _as_payload(self) -> dict:
        base = self._base_payload()
        base["delimiter"] = self.delimiter
        return base


def _flatten_transformation_from_payload(json: dict) -> Union[DtlError, Flatten]:
    if json.get(Transformation.type_field) != Flatten.type_str:
        return DtlError("Dictionary input is not of type %s" % Flatten.type_str)

    path_field = json.get("delimiter")
    if path_field is None:
        return DtlError("delimiter is missing from the json transformation")

    if not isinstance(path_field, str):
        return DtlError("delimiter should be a string")

    return Flatten(path_field)


class MapFilterNotByLabel(Transformation):
    """
    Removes data nodes with given labels.
    """

    type_str = "MapFilterNotByLabel"

    def __init__(self, labels: List[str]):
        Transformation.__init__(self, MapFilterNotByLabel.type_str)
        self.labels = labels

    def __eq__(self, other: "MapFilterNotByLabel"):
        if isinstance(self, other.__class__):
            return self._as_payload() == other._as_payload()
        return False

    def __repr__(self):
        return f"MapFilterNotByLabel(labels= {','.join(self.labels)})"

    def _as_payload(self) -> dict:
        base = self._base_payload()
        base["labels"] = self.labels
        return base


def _map_filter_not_by_label_from_payload(json: dict,) -> Union[DtlError, MapFilterNotByLabel]:
    array = _array_from_dict(json, MapFilterNotByLabel.type_str, "labels")
    if isinstance(array, DtlError):
        return array

    return MapFilterNotByLabel(array)


class MapFilterByClass(Transformation):
    """
    Keeps data nodes which are classified as one of the given classes.
    """

    type_str = "MapFilterByClass"

    def __init__(self, class_ids: List[Union[str, UUID]]):
        Transformation.__init__(self, MapFilterByClass.type_str)
        self.class_ids = class_ids

    def __eq__(self, other: "MapFilterByClass"):
        if isinstance(self, other.__class__):
            return self._as_payload() == other._as_payload()
        return False

    def __repr__(self):
        return f'MapFilterByClass(classIds= [{", ".join(map(lambda t: str(t), self.class_ids))}])'

    def _as_payload(self) -> dict:
        base = self._base_payload()
        base["classIds"] = list(map(lambda classId: str(classId), self.class_ids))
        return base


def _map_filter_by_class_from_payload(json: dict) -> Union[DtlError, MapFilterByClass]:
    array = _array_from_dict(json, MapFilterByClass.type_str, "classIds")
    if isinstance(array, DtlError):
        return array

    return MapFilterByClass(array)


class MapFilterNotByClass(Transformation):
    """
    Removes data nodes which are classified as one of the given classes.
    """

    type_str = "MapFilterNotByClass"

    def __init__(self, class_ids: List[Union[str, UUID]]):
        Transformation.__init__(self, MapFilterNotByClass.type_str)
        self.class_ids = class_ids

    def __eq__(self, other: "MapFilterNotByClass"):
        if isinstance(self, other.__class__):
            return self._as_payload() == other._as_payload()
        return False

    def __repr__(self):
        return f'MapFilterNotByClass(classIds= [{", ".join(map(lambda t: str(t), self.class_ids))}])'

    def _as_payload(self) -> dict:
        base = self._base_payload()
        base["classIds"] = list(map(lambda classId: str(classId), self.class_ids))
        return base


def _map_filter_not_by_class_from_payload(json: dict,) -> Union[DtlError, MapFilterNotByClass]:
    array = _array_from_dict(json, MapFilterNotByClass.type_str, "classIds")
    if isinstance(array, DtlError):
        return array

    return MapFilterNotByClass(array)


class MapFilterByPath(Transformation):
    """
     Keeps data nodes by given materialized paths (path from root to node). Materialized path is encoded as list of labels.
    """

    type_str = "MapFilterByPath"

    def __init__(self, paths: List[List[str]], optional_input: bool = False):
        Transformation.__init__(self, MapFilterByPath.type_str)
        self.paths = paths
        self.optional_input = optional_input

    def __eq__(self, other: "MapFilterByPath"):
        if isinstance(self, other.__class__):
            return self._as_payload() == other._as_payload()
        return False

    def __repr__(self):
        return (
            f"MapFilterByPath(paths= {','.join(map(lambda path: '.'.join(path), self.paths))}, "
            f"optional_input= {self.optional_input!r})"
        )

    def _as_payload(self) -> dict:
        base = self._base_payload()
        base["paths"] = self.paths
        base["optionalInput"] = self.optional_input
        return base


def _map_filter_by_path_from_payload(json: dict) -> Union[DtlError, MapFilterByPath]:
    if json.get(Transformation.type_field) != MapFilterByPath.type_str:
        return DtlError("Dictionary input is not of type %s" % MapFilterByPath.type_str)

    array_field = json.get("paths")
    if array_field is None:
        return DtlError("'paths' is missing from the json transformation")

    optional_input = json.get("optionalInput")
    if optional_input is None:
        optional_input = False

    array = _parse_list(_parse_string_list)(array_field)

    if isinstance(array, DtlError):
        return array

    return MapFilterByPath(array, optional_input)


class ReplaceLabel(Transformation):
    """
    Finds all nodes at the given path and replaces their label with the given one.
    """

    type_str = "ReplaceLabel"

    def __init__(self, path: List[str], replacement: str):
        Transformation.__init__(self, ReplaceLabel.type_str)
        self.path = path
        self.replacement = replacement

    def __eq__(self, other: "ReplaceLabel"):
        if isinstance(self, other.__class__):
            return self._as_payload() == other._as_payload()
        return False

    def __repr__(self):
        return f"ReplaceLabel(path= {'.'.join(self.path)}, replacement= {self.replacement})"

    def _as_payload(self) -> dict:
        base = self._base_payload()
        base["path"] = self.path
        base["replacement"] = self.replacement
        return base


def _replace_label_from_payload(json: dict) -> Union[DtlError, ReplaceLabel]:
    array = _array_from_dict(json, ReplaceLabel.type_str, "path")
    if isinstance(array, DtlError):
        return array

    replacement = json.get("replacement")
    if not isinstance(replacement, str):
        return DtlError("replacement field is not a string in %s transformation" % ReplaceLabel.type_str)

    return ReplaceLabel(array, replacement)


class ReplaceValue(Transformation):
    """
    Finds all nodes at the given path and replaces their value with the given one.
    """

    type_str = "ReplaceValue"

    def __init__(self, path: List[str], replacement: str):
        Transformation.__init__(self, ReplaceValue.type_str)
        self.path = path
        self.replacement = replacement

    def __eq__(self, other: "ReplaceValue"):
        if isinstance(self, other.__class__):
            return self._as_payload() == other._as_payload()
        return False

    def __repr__(self):
        return f"ReplaceValue(path= {'.'.join(self.path)}, replacement= {self.replacement})"

    def _as_payload(self) -> dict:
        base = self._base_payload()
        base["path"] = self.path
        base["replacement"] = self.replacement
        return base


def _replace_value_from_payload(json: dict) -> Union[DtlError, ReplaceValue]:
    array = _array_from_dict(json, ReplaceValue.type_str, "path")
    if isinstance(array, DtlError):
        return array

    replacement = json.get("replacement")
    if not isinstance(replacement, str):
        return DtlError("replacement field is not a string in %s transformation" % ReplaceValue.type_str)

    return ReplaceValue(array, replacement)


class ReplaceValueByRegex(Transformation):
    """
    Finds all nodes at the given path and replaces their value with the given one.
    """

    type_str = "ReplaceValueByRegex"

    def __init__(
        self, path: List[str], regex: Optional[str], regex_id: Optional[UUID], replacement: str,
    ):
        RegexTransformation.__init__(self, regex, regex_id, ReplaceValueByRegex.type_str)
        self.path = path
        self.regex = regex
        self.regex_id = regex_id
        self.replacement = replacement

    def __eq__(self, other: "ReplaceValueByRegex"):
        if isinstance(self, other.__class__):
            return self._as_payload() == other._as_payload()
        return False

    def __repr__(self):
        return f"ReplaceValueByRegex(path= {'.'.join(self.path)}, regex= {self.regex}, regex_id= {self.regex_id}, replacement= {self.replacement})"

    def _as_payload(self) -> dict:
        base = self._base_payload()
        base["path"] = self.path
        base["replacement"] = self.replacement
        if self.regex is not None:
            base["regex"] = self.regex
        if self.regex_id is not None:
            base["regexId"] = str(self.regex_id)
        return base


def _replace_value_by_regex_from_payload(json: dict,) -> Union[DtlError, ReplaceValueByRegex]:
    array = _array_from_dict(json, ReplaceValueByRegex.type_str, "path")
    if isinstance(array, DtlError):
        return array

    regex = json.get("regex")
    regex_id = json.get("regexId")

    if regex is None and regex_id is None:
        return _property_not_found("neither 'regex' nor 'regexId", json)

    replacement = json.get("replacement")
    if not isinstance(replacement, str):
        return DtlError("replacement field is not a string in %s transformation" % ReplaceValueByRegex.type_str)

    return ReplaceValueByRegex(array, regex, regex_id, replacement)


class ReplaceLabelByRegex(RegexTransformation):
    """
    Finds all nodes at the given path and replaces their value with the given one.
    """

    type_str = "ReplaceLabelByRegex"

    def __init__(self, regex: Optional[str], regex_id: Optional[UUID], replacement: str):
        RegexTransformation.__init__(self, regex, regex_id, ReplaceLabelByRegex.type_str)
        self.regex = regex
        self.regex_id = regex_id
        self.replacement = replacement

    def __eq__(self, other: "ReplaceLabelByRegex"):
        if isinstance(self, other.__class__):
            return self._as_payload() == other._as_payload()
        return False

    def __repr__(self):
        return f"ReplaceLabelByRegex(regex= {self.regex}, regex_id= {self.regex_id}, replacement= {self.replacement})"

    def _as_payload(self) -> dict:
        base = self._base_payload()
        base["replacement"] = self.replacement
        if self.regex is not None:
            base["regex"] = self.regex
        if self.regex_id is not None:
            base["regexId"] = str(self.regex_id)
        return base


def _replace_label_by_regex_from_payload(json: dict,) -> Union[DtlError, ReplaceLabelByRegex]:
    regex = json.get("regex")
    regex_id = json.get("regexId")

    if regex is None and regex_id is None:
        return _property_not_found("neither 'regex' nor 'regexId", json)

    replacement = json.get("replacement")
    if not isinstance(replacement, str):
        return DtlError("replacement field is not a string in %s transformation" % ReplaceLabelByRegex.type_str)

    return ReplaceLabelByRegex(regex, regex_id, replacement)


class SplitValueByRegex(RegexTransformation):
    """
    Finds all nodes at the given path which have at least one match of the given regex in their value and splits
    them into several nodes with the same label and matched substring as a value.
    """

    type_str = "SplitValueByRegex"

    def __init__(self, path: List[str], regex: Optional[str], regex_id: Optional[UUID]):
        RegexTransformation.__init__(self, regex, regex_id, SplitValueByRegex.type_str)
        self.path = path
        self.regex = regex
        self.regex_id = regex_id

    def __eq__(self, other: "SplitValueByRegex"):
        if isinstance(self, other.__class__):
            return self._as_payload() == other._as_payload()
        return False

    def __repr__(self):
        return f"SplitValueByRegex(path= {'.'.join(self.path)}, regex= {self.regex}, regex_id= {self.regex_id})"

    def _as_payload(self) -> dict:
        base = self._base_payload()
        base["path"] = self.path
        base["regex"] = self.regex
        return base


def _split_value_by_regex_from_payload(json: dict,) -> Union[DtlError, SplitValueByRegex]:
    array = _array_from_dict(json, SplitValueByRegex.type_str, "path")
    if isinstance(array, DtlError):
        return array

    regex = json.get("regex")
    regex_id = json.get("regexId")

    if regex is None and regex_id is None:
        return _property_not_found("neither 'regex' nor 'regexId", json)

    return SplitValueByRegex(array, regex, regex_id)


class Move(Transformation):
    """
    Finds all nodes at the given path and moves them as children of a new parent identified by the given to path.
    """

    type_str = "Move"

    def __init__(self, path: List[str], to: List[str]):
        Transformation.__init__(self, Move.type_str)
        self.path = path
        self.to = to

    def __eq__(self, other: "Move"):
        if isinstance(self, other.__class__):
            return self._as_payload() == other._as_payload()
        return False

    def __repr__(self):
        return f"Move(path= {'.'.join(self.path)}, to= {'.'.join(self.to)})"

    def _as_payload(self) -> dict:
        base = self._base_payload()
        base["path"] = self.path
        base["to"] = self.to
        return base


def _move_from_payload(json: dict) -> Union[DtlError, Move]:
    path = _array_from_dict(json, Move.type_str, "path")
    if isinstance(path, DtlError):
        return path

    to = _array_from_dict(json, Move.type_str, "to")
    if isinstance(to, DtlError):
        return to

    return Move(path, to)


class Copy(Transformation):
    """
    Finds all nodes at the given path and copies them as children of all nodes identified by the given to path.
    """

    type_str = "Copy"

    def __init__(self, path: List[str], to: List[str]):
        Transformation.__init__(self, Copy.type_str)
        self.path = path
        self.to = to

    def __eq__(self, other: "Copy"):
        if isinstance(self, other.__class__):
            return self._as_payload() == other._as_payload()
        return False

    def __repr__(self):
        return f"Copy(path= {'.'.join(self.path)}, to= {'.'.join(self.to)})"

    def _as_payload(self) -> dict:
        base = self._base_payload()
        base["path"] = self.path
        base["to"] = self.to
        return base


def _copy_from_payload(json: dict) -> Union[DtlError, Copy]:
    path = _array_from_dict(json, Copy.type_str, "path")
    if isinstance(path, DtlError):
        return path

    to = _array_from_dict(json, Copy.type_str, "to")
    if isinstance(to, DtlError):
        return to

    return Copy(path, to)


class CopyWithNewLabel(Transformation):
    """
    Finds all nodes at the given path and copies them to a new path ending with label
    """

    type_str = "CopyWithNewLabel"

    def __init__(self, path: List[str], to: List[str]):
        """
        :param path: the path to the target to be copied
        :param to: the path, ending with with the new label, where the target will be copied
        """
        Transformation.__init__(self, CopyWithNewLabel.type_str)
        self.path = path
        self.to = to

    def __eq__(self, other: "CopyWithNewLabel"):
        if isinstance(self, other.__class__):
            return self._as_payload() == other._as_payload()
        return False

    def __repr__(self):
        return f"CopyWithNewLabel(path= {'.'.join(self.path)}, to= {'.'.join(self.to)})"

    def _as_payload(self) -> dict:
        base = self._base_payload()
        base["path"] = self.path
        base["to"] = self.to
        return base


def _copy_with_new_label_from_payload(json: dict) -> Union[DtlError, CopyWithNewLabel]:
    path = _array_from_dict(json, CopyWithNewLabel.type_str, "path")
    if isinstance(path, DtlError):
        return path

    to = _array_from_dict(json, CopyWithNewLabel.type_str, "to")
    if isinstance(to, DtlError):
        return to

    return CopyWithNewLabel(path, to)


class RemoveEmptyBranches(Transformation):
    """
    Filters out data nodes which have no value. This operation is recursive: if all children of parent node are
     removed, the parent node is also removed.
    """

    type_str = "RemoveEmptyBranches"

    def __init__(self):
        Transformation.__init__(self, RemoveEmptyBranches.type_str)

    def __eq__(self, other: "RemoveEmptyBranches"):
        if isinstance(self, other.__class__):
            return self._as_payload() == other._as_payload()
        return False

    def __repr__(self):
        return "RemoveEmptyBranches()"

    def _as_payload(self) -> dict:
        return self._base_payload()


def _remove_empty_branches_from_payload(json: dict,) -> Union[DtlError, RemoveEmptyBranches]:
    if json.get(Transformation.type_field) != RemoveEmptyBranches.type_str:
        return DtlError("Dictionary input is not of type %s" % RemoveEmptyBranches.type_str)

    return RemoveEmptyBranches()


class ByClassReplaceValue(Transformation):
    """
    Replaces the value of data nodes that are classified as the given class
    """

    type_str = "ByClassReplaceValue"

    def __init__(self, class_id: Union[str, UUID], replacement: str):
        Transformation.__init__(self, ByClassReplaceValue.type_str)
        self.class_id = class_id
        self.replacement = replacement

    def __eq__(self, other: "ByClassReplaceValue"):
        if isinstance(self, other.__class__):
            return self._as_payload() == other._as_payload()
        return False

    def __repr__(self):
        return f"ByClassReplaceValue(classId= {str(self.class_id)}, replacement= {self.replacement})"

    def _as_payload(self) -> dict:
        base = self._base_payload()
        base["classId"] = str(self.class_id)
        base["replacement"] = self.replacement
        return base


def _by_class_replace_value_from_payload(json: dict,) -> Union[DtlError, ByClassReplaceValue]:
    class_id = json.get("classId")
    if isinstance(class_id, DtlError):
        return class_id

    replacement = json.get("replacement")
    if isinstance(replacement, DtlError):
        return replacement

    return ByClassReplaceValue(class_id, replacement)


# Custom Code Transformation & Classes


class Language(SerializableStringEnum):
    Javascript = "Javascript"

    @staticmethod
    def parse_error(s: str) -> DtlError:
        return DtlError(_enum_parse_error("language", s))

    @staticmethod
    def language_type_from_str(string: str) -> Union[DtlError, "Language"]:
        return SerializableStringEnum.from_str(Language)(string)


class ExitField:
    def __init__(self, name: str, data_type: Optional[DataType] = None, children: List["ExitField"] = None):
        """
        Represents a field output by the custom code transformation. e.g.:
        ExitField("personality", None, [
          ExitField("horoscope", DataType.String)
          ExitField("mbti", DataType.String)
        ])
        represents an exit schema with one parent field and two nested fields underneath

        :param name: name of one field of the records exiting the CustomCode transformation
        :param data_type: type of the field as an enumeration of DataType (only for children fields)
        :param children: children of the field (only for parent fields)
        """
        if children is None:
            children = []
        self.name = name
        self.data_type = data_type
        self.children = children

    def __eq__(self, other: "ExitField"):
        if isinstance(self, other.__class__):
            return self._as_payload() == other._as_payload()
        return False

    def __repr__(self):
        return f"ExitField(name= {self.name!r}, data_type= {self.data_type!r}, children= {self.children!r})"

    def _as_payload(self) -> Union[dict, DtlError]:
        if self.children and self.data_type:
            return DtlError("An exit field can have either a type (if child field) or children (if parent field)")
        if not self.children and not self.data_type:
            return DtlError("An exit field must have a type (if child field) or children (if parent field)")
        if not isinstance(self.name, str):
            return DtlError("An exit field's name must be a string.")
        if self.data_type and not isinstance(self.data_type, DataType):
            return DtlError("An exit field's datatype must be an enumeration of the DataType class.")
        # Currently only checking that it is a list, i.e. not that it is a list of ExitField(s)
        if self.children and not isinstance(self.children, List):
            return DtlError("An exit field's children must be a list of ExitField class(es).")
        base = {"name": self.name}
        if self.data_type:
            base["type"] = self.data_type.value
        else:
            base["type"] = None
        base["children"] = list(map(lambda m: m._as_payload(), self.children))
        return base

    @staticmethod
    def _from_payload(json: dict) -> Union[DtlError, "ExitField"]:
        name = json.get("name")
        data_type = json.get("type")
        if data_type is not None:
            data_type = DataType.from_str(data_type)
            if isinstance(data_type, DtlError):
                return data_type
        fields = json.get("children")
        if fields is None:
            children = []
        else:
            if not isinstance(fields, List):
                return DtlError("An exit field's children should be a list of exit fields")
            children = _parse_list(ExitField._from_payload)(fields)
        if not isinstance(name, str):
            return DtlError("An exit field's name must be a string")
        if data_type and not isinstance(data_type, DataType):
            return DtlError("If an exit field has a data_type, it must be an enumeration of the DataType class.")
        if not isinstance(children, List):
            return DtlError("If an exit field has children, it must be a list of ExitField(s)")

        return ExitField(name=name, data_type=data_type, children=children)


class CustomCode(Transformation):
    """
    Runs custom logic against the source, transforming record by record

    :param code: code defining a custom transformation logic
    :param exit_schema: structure of the records exiting the custom code transformation, as an array of ExitField(s)
    :param language: language of the user-defined transformation. Currently supported language(s): Javascript
    """

    type_str = "RunCode"

    def __init__(self, code: str, exit_schema: List[ExitField], language: Language = Language.Javascript):
        Transformation.__init__(self, CustomCode.type_str)
        self.code = code
        self.exit_schema = exit_schema
        self.language = language

    def __eq__(self, other: "CustomCode"):
        if isinstance(self, other.__class__):
            return self._as_payload() == other._as_payload()
        return False

    def __repr__(self):
        return f"CustomCode(code= {self.code!r}, exit_schema= {self.exit_schema!r}, language= {self.language!r})"

    def _as_payload(self) -> Union[dict, DtlError]:
        if not isinstance(self.code, str):
            return DtlError("Code must be formatted as a string")
        if not isinstance(self.exit_schema, List):
            return DtlError("Exit schema must be a list of ExitField(s)")
        if not isinstance(self.language, Language):
            return DtlError("Language must be a supported enumeration of the Language class")
        base = {
            "type": "RunCode",
            "code": self.code,
            "resultSchema": list(map(lambda m: m._as_payload(), self.exit_schema)),
        }
        return base

    @staticmethod
    def _from_payload(json: dict) -> Union[DtlError, "CustomCode"]:
        code = json.get("code")
        if not isinstance(code, str):
            return DtlError("code should be string")
        exit_schema = _parse_list(ExitField._from_payload)(json["resultSchema"])
        if isinstance(exit_schema, DtlError):
            return exit_schema
        return CustomCode(code=code, exit_schema=exit_schema, language=Language.Javascript)


#############################################################################################
#                                    Stream Transformations
#############################################################################################


class ElementCountSelection(Transformation):
    """
    Takes specified number of items and ignores the rest.
    """

    type_str = "ElementCountSelection"

    def __init__(self, count: int):
        Transformation.__init__(self, ElementCountSelection.type_str)
        self.count = count

    def __eq__(self, other: "ElementCountSelection"):
        if isinstance(self, other.__class__):
            return self._as_payload() == other._as_payload()
        return False

    def __repr__(self):
        return f"ElementCountSelection(count= {self.count})"

    def _as_payload(self) -> dict:
        base = self._base_payload()
        base["count"] = self.count
        return base


def _element_count_selection_from_payload(json: dict,) -> Union[DtlError, ElementCountSelection]:
    if json.get(Transformation.type_field) != ElementCountSelection.type_str:
        return DtlError("Dictionary input is not of type %s" % ElementCountSelection.type_str)

    count = json.get("count")
    if not isinstance(count, int):
        return DtlError("%s needs a count property that is an int")

    return ElementCountSelection(count)


class PathAndRegex(RegexTransformation):
    """
    Represents the associated tuple of a path with a regex
    """

    type_str = "PathAndRegex"

    def __init__(self, path: List[str], regex: Optional[str], regex_id: Optional[UUID]):
        RegexTransformation.__init__(self, regex, regex_id, PathAndRegex.type_str)
        self.path = path
        self.regex = regex
        self.regex_id = regex_id

    def __eq__(self, other: "PathAndRegex"):
        if isinstance(self, other.__class__):
            return self._as_payload() == other._as_payload()
        return False

    def __repr__(self):
        return f"(path= {'.'.join(self.path)}, regex= {self.regex}, regex_id= {self.regex_id})"

    def _as_payload(self) -> dict:
        payload = {"path": self.path}
        if self.regex is not None:
            payload["regex"] = self.regex
        if self.regex_id is not None:
            payload["regexId"] = str(self.regex_id)
        return payload


def _path_and_regex_from_payload(json: dict) -> Union[DtlError, PathAndRegex]:
    path = json.get("path")
    if path is None:
        return DtlError("path needs to be defined for %s" % str(json))

    regex = json.get("regex")
    regex_id = json.get("regexId")
    if regex is None and regex_id is None:
        return _property_not_found("neither 'regex' nor 'regexId", json)

    return PathAndRegex(path, regex, regex_id)


class FilterByPathAndRegex(Transformation):
    """
    Filters the stream and keeps items that have at least one matched node and regex from the given set
     of node path and value pairs.
    """

    type_str = "FilterByPathAndRegex"

    def __init__(self, paths_and_regex: List[PathAndRegex], optional_input: bool = False):
        Transformation.__init__(self, FilterByPathAndRegex.type_str)
        self.paths_and_regex = paths_and_regex
        self.optional_input = optional_input

    def __eq__(self, other: "FilterByPathAndRegex"):
        if isinstance(self, other.__class__):
            return self._as_payload() == other._as_payload()
        return False

    def __repr__(self):
        return (
            f"FilterByPathAndRegex(paths= {','.join(list(map(lambda x: repr(x), self.paths_and_regex)))}, "
            f"optional_input= {self.optional_input!r})"
        )

    def _as_payload(self) -> dict:
        base = self._base_payload()
        base["paths"] = list(map(lambda c: c._as_payload(), self.paths_and_regex))
        base["optionalInput"] = self.optional_input
        return base


def _filter_by_path_and_regex_from_payload(json: dict,) -> Union[DtlError, FilterByPathAndRegex]:
    if json.get(Transformation.type_field) != FilterByPathAndRegex.type_str:
        return DtlError("Dictionary input is not of type %s" % FilterByPathAndRegex.type_str)

    array_field = json.get("paths")
    if array_field is None:
        return DtlError("'paths' is missing from the json transformation")

    optional_input = json.get("optionalInput")
    if optional_input is None:
        optional_input = False

    parsed_list = _parse_list(_path_and_regex_from_payload)(array_field)
    if isinstance(parsed_list, DtlError):
        return parsed_list

    return FilterByPathAndRegex(parsed_list, optional_input)


class CompareOperators(SerializableStringEnum):
    """
    Operations that can be used to compared
    """

    Eq = "=="
    Heq = ">="
    Leq = "<="
    Les = "<"
    Hig = ">"
    Neq = "!="

    @staticmethod
    def parse_error(s: str) -> str:
        return _enum_parse_error("operator", s)

    @staticmethod
    def from_str(string: str) -> Union[DtlError, "CompareOperators"]:
        return SerializableStringEnum.from_str(CompareOperators)(string)


class FilterWithComparator(Transformation):
    """
    Keeps the elements (ADG) in the stream that satisfy the condition.
    This transformation doesn't change the ADG, it just drops elements in the stream.
    If a target node for one of the path is not a number,
    then the inequality always returns false and the element gets dropped.
    """

    type_str = "FilterWithComparator"

    def __init__(self, op: CompareOperators, left: List[str], right: List[str]):
        Transformation.__init__(self, FilterWithComparator.type_str)
        self.op = op
        self.left = left
        self.right = right

    def __eq__(self, other: "FilterWithComparator"):
        if isinstance(self, other.__class__):
            return self._as_payload() == other._as_payload()
        return False

    def __repr__(self):
        return f"FilterWithComparator(op= '{self.op}', left= {'.'.join(self.left)}, right= {'.'.join(self.right)})"

    def _as_payload(self) -> dict:
        base = self._base_payload()
        base["op"] = self.op.value
        base["left"] = self.left
        base["right"] = self.right
        return base


def _filter_with_comparator_from_payload(json: dict,) -> Union[DtlError, FilterWithComparator]:
    op = json.get("op")
    if op is None:
        return DtlError("'%s' needs a source field op")

    left = json.get("left")
    if left is None:
        return DtlError("'%s' needs a source field left")

    right = json.get("right")
    if right is None:
        return DtlError("'%s' needs a source field right")

    return FilterWithComparator(CompareOperators.from_str(op), left, right)


class FilterByClass(Transformation):
    """
    Filters the stream and keeps items that have nodes which are classified as one of the given classes.
    """

    type_str = "FilterByClass"

    def __init__(self, class_ids: List[Union[str, UUID]]):
        Transformation.__init__(self, FilterByClass.type_str)
        self.class_ids = class_ids

    def __eq__(self, other: "FilterByClass"):
        if isinstance(self, other.__class__):
            return self._as_payload() == other._as_payload()
        return False

    def __repr__(self):
        return f'FilterByClass(classIds= [{", ".join(map(lambda t: str(t), self.class_ids))}])'

    def _as_payload(self) -> dict:
        base = self._base_payload()
        base["classIds"] = list(map(lambda classId: str(classId), self.class_ids))
        return base


def _filter_by_class_from_payload(json: dict) -> Union[DtlError, FilterByClass]:
    array = _array_from_dict(json, FilterByClass.type_str, "classIds")
    if isinstance(array, DtlError):
        return array

    return FilterByClass(array)


class DropAtRandom(Transformation):
    """
    Drops items randomly from the stream
    """

    type_str = "DropAtRandom"

    def __init__(self, probability: float):
        Transformation.__init__(self, DropAtRandom.type_str)
        self.probability = probability

    def __eq__(self, other: "DropAtRandom"):
        if isinstance(self, other.__class__):
            return self._as_payload() == other._as_payload()
        return False

    def __repr__(self):
        return f"DropAtRandom(probability= {self.probability})"

    def _as_payload(self) -> dict:
        base = self._base_payload()
        base["probability"] = self.probability
        return base


def _drop_at_random_from_payload(json: dict) -> Union[DtlError, DropAtRandom]:
    if json.get(Transformation.type_field) != DropAtRandom.type_str:
        return DtlError("Dictionary input is not of type %s" % DropAtRandom.type_str)

    probability = json.get("probability")
    if not isinstance(probability, float):
        return DtlError("%s needs a probability property that is an float")

    return DropAtRandom(probability)


#############################################################################################
#                                    Joins Transformations
#############################################################################################


class FieldsToJoin:
    """
    Describes two fields on two distinct datastores, on which to join the datastores

    For every record, if the values of the two fields matches, the join occurs and the fields are merged

    :param on: the field name of the primary streaming source
    :param equals: the field name of the cached source
    """

    def __init__(self, on: List[str], equals: List[str]):
        self.on = on
        self.equals = equals

    def __repr__(self):
        return "FieldsToJoin(" + f"on={self.on!r}, " + f"equals={self.equals!r})"

    def _as_payload(self) -> dict:
        return {"on": self.on, "equals": self.equals}

    @staticmethod
    def _from_payload(json: dict) -> Union[DtlError, "FieldsToJoin"]:
        on = json.get("on")
        if not isinstance(on, list):
            return DtlError("on is not defined or is not a list")
        if not all(isinstance(field, str) for field in on):
            return DtlError("on contains something that is not a string")
        equals = json.get("equals")
        if not isinstance(equals, list):
            return DtlError("equals is not defined or is not a list")
        if not all(isinstance(field, str) for field in equals):
            return DtlError("equals contains something that is not a string")
        return FieldsToJoin(on=on, equals=equals)


class InnerJoin(Transformation):
    """
    Joins current datastore with another datastore by matched fields using  the inner join logic.
    For example, if datastore  S1 with fields A and B is joined with datastore  S2 with fields C and D where S1.B == S2.D,
    then resulting datastore  S1' will have fields A, B, C and D.
    
    It is strongly recommended to use suffixes ( cache_suffix, stream_suffix) to rename fields to avoid name 
    collisions in the join output. For example, if datasets S1 and S2 have field `id` and you join the two on that field, the output records
    will have two independent fields named `id`. If suffixes are set, then it will be easier to distinguish where each of the two `id` fields come from.
    
    Additionally, transformations can be applied to the records in the cache_source. They are executed before the join.
    
    :param cache_source_id: id of the secondary source to cache and join with the primary source of this pipeline
    :param fields_to_join: describes a number of field pairs to join on, using "and" logic between the field pairs
    :param cache_transformations: can be used to perform Transformations on the cache source before it is joined with the primary source
    :param cache_suffix: can be used add a suffix to the field names of the incoming cached source
    :param streaming_suffix: can be used add a suffix to the field names of the incoming streaming source
    :param sibling_to_field: can be used to specify the field to which the new fields will be added as a sibling. Will default to the least-nested, left-most joining field
    :param cache_source: the definition of the secondary source to cache, fetched by server-side
    :param deduplicate_join_keys: boolean flag to specify whether we want to drop (True) or keep (False) the join fields(after the join) from the cache_source.
    """

    def __init__(
        self,
        cache_source_id: Union[str, UUID],
        fields_to_join: List[FieldsToJoin],
        cache_transformations: List[Transformation] = None,
        cache_suffix: str = "",
        streaming_suffix: str = "",
        sibling_to_field: Optional[List[str]] = None,
        cache_source: Optional[Union[DatastoreDef, Datastore]] = None,
        deduplicate_join_keys: bool = True,
    ):
        Transformation.__init__(self, InnerJoin.type_str)

        self.cache_source_id = cache_source_id
        if cache_transformations is None:
            self.cache_transformations = []
        else:
            self.cache_transformations = cache_transformations
        self.fields_to_join = fields_to_join
        self.cache_suffix = cache_suffix
        self.streaming_suffix = streaming_suffix
        self.sibling_to_field = sibling_to_field
        if isinstance(cache_source, Datastore):
            cache_source = cache_source.definition
        self.cache_source = cache_source
        self.deduplicate_join_keys = deduplicate_join_keys

    type_str = "InnerJoin"

    def __eq__(self, other: "InnerJoin"):
        if isinstance(self, other.__class__):
            return self._as_payload() == other._as_payload()
        return False

    def __repr__(self):
        return (
            "InnerJoin("
            + f"cache_source_id={self.cache_source_id!r}, "
            + f"fields_to_join={self.fields_to_join!r}, "
            + f"cache_transformations={self.cache_transformations!r}, "
            + f"cache_suffix={self.cache_suffix!r}, "
            + f"streaming_suffix={self.streaming_suffix!r}"
            + (f", sibling_to_field={self.sibling_to_field!r}, " if self.sibling_to_field is not None else "")
            + (f", cache_source={self.cache_source!r}, " if self.cache_source is not None else "")
            + (f", deduplicate_join_keys={self.deduplicate_join_keys!r}")
            + ")"
        )

    def _as_payload(self) -> dict:
        base = self._base_payload()
        base["cacheSourceId"] = str(self.cache_source_id)
        base["cacheTransformations"] = list(map(lambda t: t._as_payload(), self.cache_transformations))
        base["fieldsToJoin"] = list(map(lambda f: f._as_payload(), self.fields_to_join))
        base["cacheSuffix"] = self.cache_suffix
        base["streamingSuffix"] = self.streaming_suffix
        base["siblingToField"] = self.sibling_to_field
        if self.cache_source is not None:
            base["cacheSource"] = self.cache_source._as_payload()
        base["deduplicateJoinKeys"] = self.deduplicate_join_keys
        return base


class OuterJoin(Transformation):
    """
    The version of join that uses outer join logic. SELECT ... FROM A OUTER JOIN C ON A.name = C.related_name
    """

    def __init__(
        self,
        cache_source_id: Union[str, UUID],
        fields_to_join: List[FieldsToJoin],
        cache_transformations: List[Transformation] = None,
        cache_suffix: str = "",
        streaming_suffix: str = "",
        sibling_to_field: Optional[List[str]] = None,
        optional_input: bool = False,
        cache_source: Optional[Union[DatastoreDef, Datastore]] = None,
    ):
        Transformation.__init__(self, OuterJoin.type_str)

        self.cache_source_id = cache_source_id
        if cache_transformations is None:
            self.cache_transformations = []
        else:
            self.cache_transformations = cache_transformations
        self.fields_to_join = fields_to_join
        self.cache_suffix = cache_suffix
        self.streaming_suffix = streaming_suffix
        self.sibling_to_field = sibling_to_field
        if isinstance(cache_source, Datastore):
            cache_source = cache_source.definition
        self.optional_input = optional_input
        self.cache_source = cache_source

    type_str = "OuterJoin"

    def __eq__(self, other: "OuterJoin"):
        if isinstance(self, other.__class__):
            return self._as_payload() == other._as_payload()
        return False

    def __repr__(self):
        return (
            "OuterJoin("
            + f"cache_source_id={self.cache_source_id!r}, "
            + f"fields_to_join={self.fields_to_join!r}, "
            + f"cache_transformations={self.cache_transformations!r}, "
            + f"cache_suffix={self.cache_suffix!r}, "
            + f"streaming_suffix={self.streaming_suffix!r}"
            + (f", sibling_to_field={self.sibling_to_field!r}" if self.sibling_to_field is not None else "")
            + f", optional_input={self.optional_input!r}"
            + (f", cache_source={self.cache_source!r}, " if self.cache_source is not None else "")
            + ")"
        )

    def _as_payload(self) -> dict:
        base = self._base_payload()
        base["cacheSourceId"] = str(self.cache_source_id)
        base["cacheTransformations"] = list(map(lambda t: t._as_payload(), self.cache_transformations))
        base["fieldsToJoin"] = list(map(lambda f: f._as_payload(), self.fields_to_join))
        base["cacheSuffix"] = self.cache_suffix
        base["streamingSuffix"] = self.streaming_suffix
        base["siblingToField"] = self.sibling_to_field
        base["optionalInput"] = self.optional_input
        if self.cache_source is not None:
            base["cacheSource"] = self.cache_source._as_payload()
        return base


def _join_from_payload(json: dict, join_type: str) -> Union[DtlError, OuterJoin, InnerJoin]:
    if json.get(Transformation.type_field) != join_type:
        return DtlError("Dictionary input is not of type " % join_type)

    source_field = json.get("cacheSource")
    source_id_field = json.get("cacheSourceId")
    if source_field is None and source_id_field is None:
        return DtlError("'%s' needs a source field" % join_type)

    if source_field is not None:
        source_field = _datastore_def_from_payload(source_field)
        if isinstance(source_field, DtlError):
            return source_field

    transformations_field = json.get("cacheTransformations")
    if isinstance(transformations_field, List):
        transformations_field = _parse_list(_transformation_from_payload)(transformations_field)
        if isinstance(transformations_field, DtlError):
            return transformations_field
    else:
        return DtlError("cacheTransformations is not a list")

    fields_to_join = json.get("fieldsToJoin")
    if isinstance(fields_to_join, List):
        fields_to_join = _parse_list(FieldsToJoin._from_payload)(fields_to_join)
        if isinstance(fields_to_join, DtlError):
            return fields_to_join
    else:
        return DtlError("fieldsToJoin is not a list")

    cache_suffix = json.get("cacheSuffix")
    if cache_suffix is None:
        cache_suffix = ""
    streaming_suffix = json.get("streamingSuffix")
    if streaming_suffix is None:
        streaming_suffix = ""

    if join_type == InnerJoin.type_str:
        deduplicate_join_keys = json.get("deduplicateJoinKeys")
        return InnerJoin(
            cache_source_id=source_id_field,
            fields_to_join=fields_to_join,
            cache_transformations=transformations_field,
            cache_suffix=cache_suffix,
            streaming_suffix=streaming_suffix,
            sibling_to_field=json.get("siblingToField"),
            cache_source=source_field,
            deduplicate_join_keys=deduplicate_join_keys,
        )
    else:
        optional_input = json.get("optionalInput")
        if optional_input is None:
            optional_input = False
        return OuterJoin(
            cache_source_id=source_id_field,
            fields_to_join=fields_to_join,
            cache_transformations=transformations_field,
            cache_suffix=cache_suffix,
            streaming_suffix=streaming_suffix,
            sibling_to_field=json.get("siblingToField"),
            optional_input=optional_input,
            cache_source=source_field,
        )


def _inner_join_from_payload(json: dict) -> Union[str, InnerJoin]:
    return _join_from_payload(json, InnerJoin.type_str)


def _outer_join_from_payload(json: dict) -> Union[str, OuterJoin]:
    return _join_from_payload(json, OuterJoin.type_str)


#############################################################################################
#                                    ML Transformations
#############################################################################################


class ReplaceClass:
    threshold_key = "threshold"
    new_class_key = "newClass"

    def __init__(self, threshold: float, new_class: str):
        self.threshold = threshold
        self.new_class = new_class

    def __repr__(self):
        return f"ReplaceClass(threshold= {self.threshold}, newClass= {self.new_class})"

    def __eq__(self, other: "ReplaceClass"):
        if isinstance(self, other.__class__):
            return self.threshold == other.threshold and self.new_class == other.new_class
        return False


class Segment(Transformation):
    type_str = "Segment"

    def __init__(self, class_ids: List[Union[str, UUID]]):
        Transformation.__init__(self, Segment.type_str)
        self.class_ids = class_ids

    def __eq__(self, other: "Segment"):
        if isinstance(self, other.__class__):
            return self._as_payload() == other._as_payload()
        return False

    def __repr__(self):
        return f"Segment(classIds= {'.'.join(map(lambda t: str(t), self.class_ids))})"

    def _as_payload(self) -> dict:
        base = self._base_payload()
        base["classIds"] = list(map(lambda classId: str(classId), self.class_ids))
        return base

    @staticmethod
    def _from_payload(json: dict) -> Union[DtlError, "Segment"]:
        class_ids = json.get("classIds")
        if class_ids is None:
            return _property_not_found("classIds", json)

        class_ids = _parse_string_list(class_ids)
        if isinstance(class_ids, DtlError):
            return class_ids

        return Segment(class_ids)


class FoldClassifications(Transformation):
    """
    Analyzes the classification information of every ADG in the stream and fold the statistics of all
    """

    type_str = "FoldClassifications"

    def __init__(self):
        Transformation.__init__(self, FoldClassifications.type_str)

    def __eq__(self, other: "FoldClassifications"):
        if isinstance(self, other.__class__):
            return self._as_payload() == other._as_payload()
        return False

    def __repr__(self):
        return "FoldClassifications()"

    def _as_payload(self) -> dict:
        return self._base_payload()

    @staticmethod
    def _from_payload(json: dict) -> Union[DtlError, "FoldClassifications"]:
        if json.get(Transformation.type_field) != FoldClassifications.type_str:
            return DtlError("Dictionary input is not of type %s" % FoldClassifications.type_str)

        return FoldClassifications()


_transformations = dict(
    [
        (MapFunction.type_str, MapFunction._from_payload),
        (Split.type_str, _split_transformation_from_payload),
        (SplitLabelAndValue.type_str, SplitLabelAndValue._from_payload),
        (MoveByRegex.type_str, MoveByRegex._from_payload),
        (Flatten.type_str, _flatten_transformation_from_payload),
        (MapFilterNotByLabel.type_str, _map_filter_not_by_label_from_payload),
        (MapFilterByClass.type_str, _map_filter_by_class_from_payload),
        (MapFilterNotByClass.type_str, _map_filter_not_by_class_from_payload),
        (MapFilterByPath.type_str, _map_filter_by_path_from_payload),
        (ReplaceLabel.type_str, _replace_label_from_payload),
        (ReplaceValue.type_str, _replace_value_from_payload),
        (ReplaceLabelByRegex.type_str, _replace_label_by_regex_from_payload),
        (ReplaceValueByRegex.type_str, _replace_value_by_regex_from_payload),
        (SplitValueByRegex.type_str, _split_value_by_regex_from_payload),
        (Move.type_str, _move_from_payload),
        (Copy.type_str, _copy_from_payload),
        (CopyWithNewLabel.type_str, _copy_with_new_label_from_payload),
        (RemoveEmptyBranches.type_str, _remove_empty_branches_from_payload),
        (ByClassReplaceValue.type_str, _by_class_replace_value_from_payload),
        (ElementCountSelection.type_str, _element_count_selection_from_payload),
        (FilterByPathAndRegex.type_str, _filter_by_path_and_regex_from_payload),
        (FilterByClass.type_str, _filter_by_class_from_payload),
        (DropAtRandom.type_str, _drop_at_random_from_payload),
        (InnerJoin.type_str, _inner_join_from_payload),
        (OuterJoin.type_str, _outer_join_from_payload),
        (Classify.type_str, Classify._from_payload),
        (Add.type_str, Add._from_payload),
        (Math.type_str, Math._from_payload),
        (ToDate.type_str, ToDate._from_payload),
        (ToInt.type_str, ToInt._from_payload),
        (ToDouble.type_str, ToDouble._from_payload),
        (ToUUID.type_str, ToUUID._from_payload),
        (AppendIndexToLabel.type_str, AppendIndexToLabel._from_payload),
        (Structure.type_str, Structure._from_payload),
        (Segment.type_str, Segment._from_payload),
        (FilterWithComparator.type_str, _filter_with_comparator_from_payload),
        (FlatMap.type_str, FlatMap._from_payload),
        (ConcatenateAtPaths.type_str, ConcatenateAtPaths._from_payload),
        (FoldClassifications.type_str, FoldClassifications._from_payload),
        (Obfuscate.type_str, Obfuscate._from_payload),
        (Decrypt.type_str, Decrypt._from_payload),
        (MergeFields.type_str, MergeFields._from_payload),
        (JsonStringify.type_str, JsonStringify._from_payload),
        (AddWithCustomValue.type_str, AddWithCustomValue._from_payload),
        (CustomCode.type_str, CustomCode._from_payload),
        (FormatDate.type_str, FormatDate._from_payload),
        (ToMacAddress.type_str, ToMacAddress._from_payload),
    ]
)


def _transformation_from_payload(json: dict) -> Union[DtlError, Transformation]:
    type_field = json.get(Transformation.type_field)
    if type_field is None:
        return DtlError("The json object doesn't have a '%s' property" % Transformation.type_field)

    parsing_function = _transformations.get(type_field)
    if parsing_function is None:
        return DtlError("Looks like '%s' transformation is not handled by the SDK" % type_field)

    return parsing_function(json)
